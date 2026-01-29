from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View

from ..constants.combat import CombatAction, CombatState
from ..models.combat import Combat, Turn
from ..models.events import ActionTaken
from ..models.game import Actor
from ..utils.channels import send_to_channel
from .mixins import GameContextMixin


class InitiativeTrackerMixin:
    """Mixin providing initiative tracker rendering utilities."""

    def get_tracker_context(self, combat, user):
        """Build fighter data with HP, conditions, and current turn status."""
        fighters_data = []
        initiative_order = combat.get_initiative_order()

        for fighter in initiative_order:
            character = fighter.character
            is_current = fighter == combat.current_fighter
            is_player_turn = (
                is_current
                and hasattr(fighter.player, "user")
                and fighter.player.user == user
            )

            # Get active conditions for the character
            conditions = list(
                character.active_conditions.select_related("condition").all()
            )

            fighters_data.append(
                {
                    "fighter": fighter,
                    "character": character,
                    "initiative": fighter.dexterity_check,
                    "is_current": is_current,
                    "is_surprised": fighter.is_surprised,
                    "is_player_turn": is_player_turn,
                    "is_owned_by_user": (
                        hasattr(fighter.player, "user") and fighter.player.user == user
                    ),
                    "hp": character.hp,
                    "max_hp": character.max_hp,
                    "hp_percentage": character.hp_percentage,
                    "conditions": conditions,
                }
            )

        return {
            "combat": combat,
            "fighters": fighters_data,
            "current_round": combat.current_round,
        }

    def render_tracker(self, combat, user, game, animation=""):
        """Return rendered HTML for the initiative tracker."""
        context = self.get_tracker_context(combat, user)
        context["animation"] = animation
        context["game"] = game
        context["user"] = user
        context["is_dm"] = game.master.user == user

        html = render_to_string("game/partials/initiative_tracker.html", context)
        return html


class InitiativeTrackerView(
    LoginRequiredMixin, InitiativeTrackerMixin, GameContextMixin, View
):
    """View for rendering the initiative tracker."""

    def get(self, request, *args, **kwargs):
        combat_id = kwargs.get("combat_id")
        try:
            combat = Combat.objects.get(id=combat_id, game=self.game)
        except Combat.DoesNotExist:
            return HttpResponse("")

        if combat.state != CombatState.ACTIVE:
            return HttpResponse("")

        html = self.render_tracker(combat, request.user, self.game)
        return HttpResponse(html)


class ReadyActionView(
    UserPassesTestMixin, InitiativeTrackerMixin, GameContextMixin, View
):
    """View for taking the Ready action during combat."""

    def test_func(self):
        """Verify it's the player's turn."""
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

    def post(self, request, *args, **kwargs):
        combat_id = kwargs.get("combat_id")
        combat = Combat.objects.get(id=combat_id, game=self.game)
        fighter = combat.current_fighter

        # Get the current turn
        turn = Turn.objects.filter(
            fighter=fighter,
            round__combat=combat,
            completed=False,
        ).first()

        if not turn:
            return HttpResponse("No active turn", status=400)

        if not turn.can_take_action():
            return HttpResponse("Action already used", status=400)

        # Use the READY action
        turn_action = turn.use_action(CombatAction.READY)

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

        # Return updated tracker with animation
        html = self.render_tracker(combat, request.user, self.game, animation="ready")
        response = HttpResponse(html)
        response["HX-Trigger"] = "initiative-updated"
        return response


class DelayTurnView(
    UserPassesTestMixin, InitiativeTrackerMixin, GameContextMixin, View
):
    """View for delaying turn (skipping without using resources)."""

    def test_func(self):
        """Verify it's the player's turn."""
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

    def post(self, request, *args, **kwargs):
        combat_id = kwargs.get("combat_id")
        combat = Combat.objects.get(id=combat_id, game=self.game)

        # Advance to next turn (skipping current player)
        combat.advance_turn()

        # Return updated tracker with animation
        html = self.render_tracker(combat, request.user, self.game, animation="delay")
        response = HttpResponse(html)
        response["HX-Trigger"] = "initiative-updated"
        return response
