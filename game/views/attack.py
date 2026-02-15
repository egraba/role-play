from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View

from equipment.models.equipment import Weapon
from magic.models.spells import Concentration

from ..attack import apply_damage, get_attack_ability, resolve_attack
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
        targets = Fighter.objects.filter(combat=combat).exclude(id=fighter.id)
        character = fighter.character

        # Get weapons from character's inventory
        weapons = Weapon.objects.filter(inventory=character.inventory).select_related(
            "settings"
        )

        # Calculate attack bonus per weapon for display
        weapon_data = []
        for weapon in weapons:
            ability_name = get_attack_ability(weapon, character)
            ability = character.abilities.filter(
                ability_type__name=ability_name
            ).first()
            ability_modifier = ability.modifier if ability else 0
            proficiency = getattr(character, "proficiency_bonus", 2)
            attack_bonus = ability_modifier + proficiency
            weapon_data.append(
                {
                    "weapon": weapon,
                    "attack_bonus": attack_bonus,
                    "ability": ability_name,
                    "damage": weapon.settings.damage or "1d4",
                }
            )

        return {
            "combat": combat,
            "fighter": fighter,
            "targets": targets,
            "weapons": weapon_data,
            "attack_bonus": weapon_data[0]["attack_bonus"] if weapon_data else 0,
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
        weapon_id = request.POST.get("weapon_id")
        roll_modifier = request.POST.get("roll_modifier", "normal")

        # Validate target
        try:
            target = Fighter.objects.get(id=target_id, combat=combat)
        except Fighter.DoesNotExist:
            context = self.get_attack_context(combat, request.user, fighter)
            context["error"] = "Invalid target selected"
            return HttpResponse(self.render_attack_modal(context, self.game))

        # Validate weapon
        try:
            weapon = Weapon.objects.get(
                id=weapon_id, inventory=fighter.character.inventory
            )
        except Weapon.DoesNotExist:
            context = self.get_attack_context(combat, request.user, fighter)
            context["error"] = "Invalid weapon selected"
            return HttpResponse(self.render_attack_modal(context, self.game))

        # Resolve the attack using the service module
        result = resolve_attack(
            attacker=fighter.character,
            target=target.character,
            weapon=weapon,
            advantage=(roll_modifier == "advantage"),
            disadvantage=(roll_modifier == "disadvantage"),
        )

        # Build damage formula for display
        damage_formula = ""
        if result.damage_rolls:
            rolls_str = "+".join(map(str, result.damage_rolls))
            dice_count = len(result.damage_rolls)
            die_size = (
                result.damage_dice.split("d")[-1] if "d" in result.damage_dice else "?"
            )
            damage_formula = (
                f"{dice_count}d{die_size} ({rolls_str}) + {result.damage_modifier}"
            )

        # Build result context
        context = self.get_attack_context(combat, request.user, fighter)
        context.update(
            {
                "attack_result": True,
                "target": target,
                "natural_roll": result.natural_roll,
                "second_roll": result.second_natural_roll,
                "roll_modifier": roll_modifier,
                "attack_bonus": result.attack_modifier,
                "total_roll": result.attack_roll,
                "is_hit": result.is_hit,
                "is_critical_hit": result.is_critical_hit,
                "is_critical_miss": result.is_critical_miss,
                "weapon_name": result.weapon_name,
                "weapon_id": weapon.id,
                # Pre-computed damage (displayed in DamageRollView)
                "damage_rolls": result.damage_rolls,
                "damage_formula": damage_formula,
                "total_damage": result.damage,
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
        """Display pre-computed damage results."""
        combat_id = kwargs.get("combat_id")
        combat = Combat.objects.get(id=combat_id, game=self.game)
        fighter = combat.current_fighter

        target_id = request.POST.get("target_id")
        is_critical = request.POST.get("is_critical") == "true"
        natural_roll = int(request.POST.get("natural_roll", 0))
        total_roll = int(request.POST.get("total_roll", 0))
        attack_bonus = int(request.POST.get("attack_bonus", 0))
        total_damage = int(request.POST.get("total_damage", 0))
        damage_rolls_str = request.POST.get("damage_rolls", "")
        damage_formula = request.POST.get("damage_formula", "")

        try:
            target = Fighter.objects.get(id=target_id, combat=combat)
        except Fighter.DoesNotExist:
            return HttpResponse("Invalid target", status=400)

        # Parse damage rolls from comma-separated string
        damage_rolls = [int(d) for d in damage_rolls_str.split(",") if d.strip()]

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
                "damage_dice": damage_rolls,
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

        # Apply damage to target character using the service module
        target_character = target.character
        apply_damage(target_character, damage)

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
