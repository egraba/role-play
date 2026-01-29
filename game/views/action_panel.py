from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View

from ..constants.combat import CombatAction, CombatState
from ..models.combat import Combat, Turn
from .mixins import GameContextMixin


# Action definitions with labels, icons, and descriptions
ACTION_DEFINITIONS = [
    {
        "value": CombatAction.ATTACK,
        "label": "Attack",
        "icon": "attack",
        "description": "Make one melee or ranged attack. You may be able to make multiple attacks with the Extra Attack feature.",
    },
    {
        "value": CombatAction.CAST_SPELL,
        "label": "Cast Spell",
        "icon": "cast-spell",
        "description": "Cast a spell with a casting time of 1 action. See the spell's description for its effects.",
    },
    {
        "value": CombatAction.DASH,
        "label": "Dash",
        "icon": "dash",
        "description": "Gain extra movement equal to your speed for the current turn. This is added to any movement you already have.",
    },
    {
        "value": CombatAction.DISENGAGE,
        "label": "Disengage",
        "icon": "disengage",
        "description": "Your movement doesn't provoke opportunity attacks for the rest of the turn.",
    },
    {
        "value": CombatAction.DODGE,
        "label": "Dodge",
        "icon": "dodge",
        "description": "Until your next turn, attack rolls against you have disadvantage (if you can see the attacker), and you make DEX saves with advantage.",
    },
    {
        "value": CombatAction.HELP,
        "label": "Help",
        "icon": "help",
        "description": "Aid an ally in attacking a creature or with an ability check. The ally gains advantage on their next roll.",
    },
    {
        "value": CombatAction.HIDE,
        "label": "Hide",
        "icon": "hide",
        "description": "Make a Dexterity (Stealth) check to hide. If successful, you gain the benefits of being unseen.",
    },
    {
        "value": CombatAction.READY,
        "label": "Ready",
        "icon": "ready",
        "description": "Prepare to act later. Choose a trigger and an action/spell to take when it occurs (uses your reaction).",
    },
    {
        "value": CombatAction.SEARCH,
        "label": "Search",
        "icon": "search",
        "description": "Make a Wisdom (Perception) or Intelligence (Investigation) check to find something hidden.",
    },
    {
        "value": CombatAction.USE_OBJECT,
        "label": "Use Object",
        "icon": "defend",
        "description": "Interact with a second object or use an object that requires an action, such as drinking a potion.",
    },
]


class ActionPanelMixin:
    """Mixin providing action panel rendering utilities."""

    def get_panel_context(self, combat, user):
        """Build context for the action panel."""
        current_fighter = combat.current_fighter
        is_player_turn = (
            current_fighter
            and hasattr(current_fighter.player, "user")
            and current_fighter.player.user == user
        )

        # Get the current turn
        turn = None
        actions_taken = []
        if current_fighter:
            turn = Turn.objects.filter(
                fighter=current_fighter,
                round__combat=combat,
                completed=False,
            ).first()
            if turn:
                actions_taken = list(turn.actions.all())

        # Create a turn-like object if turn is None (for template safety)
        if not turn:

            class MockTurn:
                action_used = True
                bonus_action_used = True
                reaction_used = True
                movement_used = 30
                movement_total = 30

                def remaining_movement(self):
                    return 0

            turn = MockTurn()

        return {
            "combat": combat,
            "turn": turn,
            "is_player_turn": is_player_turn,
            "standard_actions": ACTION_DEFINITIONS,
            "actions_taken": actions_taken,
        }

    def render_panel(self, combat, user, game):
        """Return rendered HTML for the action panel."""
        context = self.get_panel_context(combat, user)
        context["game"] = game
        context["user"] = user

        html = render_to_string("game/partials/action_panel.html", context)
        return html


class ActionPanelView(LoginRequiredMixin, ActionPanelMixin, GameContextMixin, View):
    """View for rendering the action panel."""

    def get(self, request, *args, **kwargs):
        combat_id = kwargs.get("combat_id")
        try:
            combat = Combat.objects.get(id=combat_id, game=self.game)
        except Combat.DoesNotExist:
            return HttpResponse("")

        if combat.state != CombatState.ACTIVE:
            return HttpResponse("")

        html = self.render_panel(combat, request.user, self.game)
        return HttpResponse(html)
