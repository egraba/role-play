from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse, JsonResponse
from django.views import View

from ..constants.combat import ActionType, CombatAction, CombatState
from ..exceptions import ActionNotAvailable
from ..models.combat import Combat, Fighter, Turn
from ..models.events import ActionTaken
from ..models.game import Actor
from ..utils.channels import send_to_channel
from .action_panel import ActionPanelMixin
from .mixins import GameContextMixin


class TakeActionView(UserPassesTestMixin, ActionPanelMixin, GameContextMixin, View):
    """View for a player to take an action during their turn."""

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

        action = request.POST.get("action")
        target_id = request.POST.get("target_id")
        action_type = request.POST.get("action_type", ActionType.ACTION)

        # Check if this is an HTMX request
        is_htmx = request.headers.get("HX-Request") == "true"

        if action not in CombatAction.values:
            if is_htmx:
                return HttpResponse("Invalid action", status=400)
            return JsonResponse(
                {"status": "error", "message": "Invalid action"}, status=400
            )

        # Get the current turn
        turn = Turn.objects.filter(
            fighter=fighter,
            round__combat=combat,
            completed=False,
        ).first()

        if not turn:
            if is_htmx:
                return HttpResponse("No active turn found", status=400)
            return JsonResponse(
                {"status": "error", "message": "No active turn found"}, status=400
            )

        # Get target fighter if specified
        target_fighter = None
        if target_id:
            try:
                target_fighter = Fighter.objects.get(id=target_id, combat=combat)
            except Fighter.DoesNotExist:
                if is_htmx:
                    return HttpResponse("Invalid target", status=400)
                return JsonResponse(
                    {"status": "error", "message": "Invalid target"}, status=400
                )

        # Execute the action based on type
        try:
            if action_type == ActionType.ACTION:
                turn_action = turn.use_action(action, target_fighter)
            elif action_type == ActionType.BONUS_ACTION:
                turn_action = turn.use_bonus_action(action, target_fighter)
            elif action_type == ActionType.REACTION:
                turn_action = turn.use_reaction(action, target_fighter)
            else:
                if is_htmx:
                    return HttpResponse("Invalid action type", status=400)
                return JsonResponse(
                    {"status": "error", "message": "Invalid action type"}, status=400
                )
        except ActionNotAvailable as e:
            if is_htmx:
                return HttpResponse(str(e), status=400)
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

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

        # Return updated action panel for HTMX requests
        if is_htmx:
            html = self.render_panel(combat, request.user, self.game)
            response = HttpResponse(html)
            response["HX-Trigger"] = "action-taken"
            return response

        return JsonResponse({"status": "ok", "action_id": turn_action.id})


class TurnStateView(GameContextMixin, View):
    """Returns current turn state for the active combat."""

    def get(self, request, *args, **kwargs):
        combat_id = kwargs.get("combat_id")
        try:
            combat = Combat.objects.get(id=combat_id, game=self.game)
        except Combat.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Combat not found"}, status=404
            )

        if combat.state != CombatState.ACTIVE:
            return JsonResponse(
                {"status": "error", "message": "Combat not active"}, status=400
            )

        current_fighter = combat.current_fighter
        if not current_fighter:
            return JsonResponse(
                {"status": "error", "message": "No current fighter"}, status=400
            )

        turn = Turn.objects.filter(
            fighter=current_fighter,
            round__combat=combat,
            completed=False,
        ).first()

        if not turn:
            return JsonResponse(
                {"status": "error", "message": "No active turn"}, status=400
            )

        return JsonResponse(
            {
                "fighter": current_fighter.character.name,
                "fighter_id": current_fighter.id,
                "round": combat.current_round,
                "action_available": turn.can_take_action(),
                "bonus_action_available": turn.can_take_bonus_action(),
                "reaction_available": turn.can_take_reaction(),
                "movement_remaining": turn.remaining_movement(),
                "movement_total": turn.movement_total,
                "actions_taken": [
                    {
                        "action": a.action,
                        "action_display": a.get_action_display(),
                        "type": a.action_type,
                        "type_display": a.get_action_type_display(),
                        "target": str(a.target_fighter) if a.target_fighter else None,
                    }
                    for a in turn.actions.all()
                ],
            }
        )


class MoveView(UserPassesTestMixin, ActionPanelMixin, GameContextMixin, View):
    """View for a player to use movement during their turn."""

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

        # Check if this is an HTMX request
        is_htmx = request.headers.get("HX-Request") == "true"

        try:
            feet = int(request.POST.get("feet", 0))
        except (ValueError, TypeError):
            if is_htmx:
                return HttpResponse("Invalid feet value", status=400)
            return JsonResponse(
                {"status": "error", "message": "Invalid feet value"}, status=400
            )

        if feet <= 0:
            if is_htmx:
                return HttpResponse("Feet must be positive", status=400)
            return JsonResponse(
                {"status": "error", "message": "Feet must be positive"}, status=400
            )

        turn = Turn.objects.filter(
            fighter=fighter,
            round__combat=combat,
            completed=False,
        ).first()

        if not turn:
            if is_htmx:
                return HttpResponse("No active turn found", status=400)
            return JsonResponse(
                {"status": "error", "message": "No active turn found"}, status=400
            )

        actual_moved = turn.use_movement(feet)

        # Return updated action panel for HTMX requests
        if is_htmx:
            html = self.render_panel(combat, request.user, self.game)
            return HttpResponse(html)

        return JsonResponse(
            {
                "status": "ok",
                "feet_moved": actual_moved,
                "movement_remaining": turn.remaining_movement(),
            }
        )
