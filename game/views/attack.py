import random

from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View

from magic.models.spells import Concentration

from ..constants.combat import CombatAction, CombatState
from ..models.combat import Combat, Fighter, Turn
from ..models.events import ActionTaken
from ..models.game import Actor
from ..utils.channels import send_to_channel
from .action_panel import ActionPanelMixin
from .concentration import check_concentration_on_damage
from .mixins import GameContextMixin


class CombatTurnPermissionMixin(UserPassesTestMixin):
    """Mixin that verifies the requesting user is the current fighter in active combat."""

    def test_func(self) -> bool:
        combat_id = self.kwargs.get("combat_id")
        try:
            combat = Combat.objects.get(id=combat_id, game=self.game)
            if combat.state != CombatState.ACTIVE:
                return False
            current_fighter = combat.current_fighter
            if not current_fighter:
                return False
            return current_fighter.player.user == self.request.user
        except Combat.DoesNotExist:
            return False


class AttackModalMixin:
    """Mixin providing attack modal rendering utilities."""

    def get_attack_context(self, combat, user, fighter):
        """Build base context for the attack modal."""
        # Get potential targets (all fighters except the attacker)
        targets = Fighter.objects.filter(combat=combat).exclude(id=fighter.id)

        # Calculate attack bonus from character
        character = fighter.character

        # Get strength modifier (Ability object has .modifier property)
        try:
            str_modifier = character.strength.modifier
        except (AttributeError, character.abilities.model.DoesNotExist):
            str_modifier = 0

        # Use character's proficiency_bonus property
        proficiency = getattr(character, "proficiency_bonus", 2)

        attack_bonus = str_modifier + proficiency

        return {
            "combat": combat,
            "fighter": fighter,
            "targets": targets,
            "attack_bonus": attack_bonus,
            "show_modal": True,
        }

    def render_attack_modal(self, context, game):
        """Render the attack modal HTML."""
        context["game"] = game
        return render_to_string("game/partials/attack_modal.html", context)


class AttackModalView(
    CombatTurnPermissionMixin, AttackModalMixin, GameContextMixin, View
):
    """View for displaying the attack modal."""

    def get(self, request, *args, **kwargs):
        """Show the attack modal with target selection."""
        combat_id = kwargs.get("combat_id")
        combat = Combat.objects.get(id=combat_id, game=self.game)
        fighter = combat.current_fighter

        context = self.get_attack_context(combat, request.user, fighter)
        html = self.render_attack_modal(context, self.game)

        return HttpResponse(html)


class AttackRollView(
    CombatTurnPermissionMixin, AttackModalMixin, GameContextMixin, View
):
    """View for processing the attack roll."""

    def post(self, request, *args, **kwargs):
        """Process the attack roll and return results."""
        combat_id = kwargs.get("combat_id")
        combat = Combat.objects.get(id=combat_id, game=self.game)
        fighter = combat.current_fighter

        target_id = request.POST.get("target_id")
        roll_modifier = request.POST.get("roll_modifier", "normal")

        # Validate target
        try:
            target = Fighter.objects.get(id=target_id, combat=combat)
        except Fighter.DoesNotExist:
            context = self.get_attack_context(combat, request.user, fighter)
            context["error"] = "Invalid target selected"
            return HttpResponse(self.render_attack_modal(context, self.game))

        # Get attack bonus
        character = fighter.character
        try:
            str_modifier = character.strength.modifier
        except (AttributeError, character.abilities.model.DoesNotExist):
            str_modifier = 0
        proficiency = getattr(character, "proficiency_bonus", 2)
        attack_bonus = str_modifier + proficiency

        # Roll the d20
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20) if roll_modifier != "normal" else None

        # Determine which roll to use
        if roll_modifier == "advantage":
            natural_roll = max(roll1, roll2)
            second_roll = min(roll1, roll2)
        elif roll_modifier == "disadvantage":
            natural_roll = min(roll1, roll2)
            second_roll = max(roll1, roll2)
        else:
            natural_roll = roll1
            second_roll = None

        total_roll = natural_roll + attack_bonus

        # Determine hit/miss (ac field, not armor_class)
        target_ac = getattr(target.character, "ac", 10) or 10
        is_critical_hit = natural_roll == 20
        is_critical_miss = natural_roll == 1
        is_hit = is_critical_hit or (not is_critical_miss and total_roll >= target_ac)

        # Build result context
        context = self.get_attack_context(combat, request.user, fighter)
        context.update(
            {
                "attack_result": True,
                "target": target,
                "natural_roll": natural_roll,
                "second_roll": second_roll,
                "roll_modifier": roll_modifier,
                "attack_bonus": attack_bonus,
                "total_roll": total_roll,
                "is_hit": is_hit,
                "is_critical_hit": is_critical_hit,
                "is_critical_miss": is_critical_miss,
                "animate": True,
            }
        )

        html = self.render_attack_modal(context, self.game)
        return HttpResponse(html)


class DamageRollView(
    CombatTurnPermissionMixin, AttackModalMixin, GameContextMixin, View
):
    """View for processing the damage roll."""

    def post(self, request, *args, **kwargs):
        """Process the damage roll."""
        combat_id = kwargs.get("combat_id")
        combat = Combat.objects.get(id=combat_id, game=self.game)
        fighter = combat.current_fighter

        target_id = request.POST.get("target_id")
        is_critical = request.POST.get("is_critical") == "true"
        natural_roll = int(request.POST.get("natural_roll", 0))
        total_roll = int(request.POST.get("total_roll", 0))

        # Validate target
        try:
            target = Fighter.objects.get(id=target_id, combat=combat)
        except Fighter.DoesNotExist:
            return HttpResponse("Invalid target", status=400)

        # Get attack bonus for display
        character = fighter.character
        try:
            str_modifier = character.strength.modifier
        except (AttributeError, character.abilities.model.DoesNotExist):
            str_modifier = 0
        proficiency = getattr(character, "proficiency_bonus", 2)
        attack_bonus = str_modifier + proficiency

        # Roll damage - default to 1d8 (longsword) + STR modifier
        # This could be extended to use actual weapon damage dice
        num_dice = 2 if is_critical else 1  # Double dice on crit
        damage_dice = [random.randint(1, 8) for _ in range(num_dice)]
        base_damage = sum(damage_dice)
        total_damage = base_damage + str_modifier

        # Ensure minimum 1 damage
        total_damage = max(1, total_damage)

        # Build damage formula string
        if is_critical:
            damage_formula = f"2d8 ({'+'.join(map(str, damage_dice))}) + {str_modifier}"
        else:
            damage_formula = f"1d8 ({damage_dice[0]}) + {str_modifier}"

        # Build result context
        context = self.get_attack_context(combat, request.user, fighter)
        context.update(
            {
                "attack_result": True,
                "target": target,
                "natural_roll": natural_roll,
                "attack_bonus": attack_bonus,
                "total_roll": total_roll,
                "is_hit": True,
                "is_critical_hit": is_critical,
                "is_critical_miss": False,
                "damage_rolled": True,
                "damage_dice": damage_dice,
                "damage_formula": damage_formula,
                "total_damage": total_damage,
            }
        )

        html = self.render_attack_modal(context, self.game)
        return HttpResponse(html)


class ApplyDamageView(
    CombatTurnPermissionMixin,
    ActionPanelMixin,
    AttackModalMixin,
    GameContextMixin,
    View,
):
    """View for applying damage to a target."""

    def post(self, request, *args, **kwargs):
        """Apply damage to target and use the action."""
        combat_id = kwargs.get("combat_id")
        combat = Combat.objects.get(id=combat_id, game=self.game)
        fighter = combat.current_fighter

        target_id = request.POST.get("target_id")
        damage = int(request.POST.get("damage", 0))

        # Validate target
        try:
            target = Fighter.objects.get(id=target_id, combat=combat)
        except Fighter.DoesNotExist:
            return HttpResponse("Invalid target", status=400)

        # Apply damage to target character using the take_damage method
        target_character = target.character
        target_character.take_damage(damage)

        # Use the action
        turn = Turn.objects.filter(
            fighter=fighter,
            round__combat=combat,
            completed=False,
        ).first()

        if turn and turn.can_take_action():
            turn_action = turn.use_action(CombatAction.ATTACK, target)

            # Create and broadcast event
            author = Actor.objects.get(
                player__game=self.game, player__user=self.request.user
            )
            action_event = ActionTaken.objects.create(
                game=self.game,
                author=author,
                combat=combat,
                fighter=fighter,
                turn_action=turn_action,
            )
            send_to_channel(action_event)

        # Check if target has concentration and needs to make a save
        concentration_info = None
        try:
            if target_character.concentration:
                concentration_info = check_concentration_on_damage(
                    game=self.game,
                    character=target_character,
                    damage=damage,
                    author=author,
                )
        except Concentration.DoesNotExist:
            pass

        # Build confirmation context
        context = self.get_attack_context(combat, request.user, fighter)
        context.update(
            {
                "damage_applied": damage,
                "target": target,
                "concentration_info": concentration_info,
            }
        )

        html = self.render_attack_modal(context, self.game)
        response = HttpResponse(html)
        response["HX-Trigger"] = "damage-applied, initiative-updated"
        return response
