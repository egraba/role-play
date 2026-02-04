import re

from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View

from utils.dice import DiceString, DiceStringFormatError

from ..services import DiceRollService
from .mixins import GameContextMixin

# Regex to parse dice expressions like "1d20+5", "2d6-1", "d8"
DICE_EXPR_REGEX = re.compile(r"^(\d+)?d(\d+)([+-]\d+)?$", re.IGNORECASE)


class DiceRollerModalView(UserPassesTestMixin, GameContextMixin, View):
    """View for displaying the dice roller modal."""

    def test_func(self):
        """Verify user is a participant in the game."""
        return self.is_user_master() or self.is_user_player()

    def get(self, request, *args, **kwargs):
        """Show the dice roller modal."""
        context = {
            "game": self.game,
            "show_modal": True,
            "dice_types": [
                {"value": 4, "label": "d4", "color": "#e74c3c"},
                {"value": 6, "label": "d6", "color": "#3498db"},
                {"value": 8, "label": "d8", "color": "#2ecc71"},
                {"value": 10, "label": "d10", "color": "#e67e22"},
                {"value": 12, "label": "d12", "color": "#9b59b6"},
                {"value": 20, "label": "d20", "color": "#f1c40f"},
            ],
        }
        html = render_to_string("game/partials/dice_roller_modal.html", context)
        return HttpResponse(html)


class DiceRollView(UserPassesTestMixin, GameContextMixin, View):
    """View for processing dice rolls."""

    def test_func(self):
        """Verify user is a participant in the game."""
        return self.is_user_master() or self.is_user_player()

    def post(self, request, *args, **kwargs):
        """Process the dice roll and return results."""
        dice_type = int(request.POST.get("dice_type", 20))
        num_dice = int(request.POST.get("num_dice", 1))
        modifier = int(request.POST.get("modifier", 0))
        roll_purpose = request.POST.get("roll_purpose", "").strip()

        # Clamp values
        num_dice = max(1, min(10, num_dice))
        modifier = max(-20, min(20, modifier))

        # Build dice notation
        dice_notation = f"{num_dice}d{dice_type}"

        try:
            dice = DiceString(dice_notation)
            total, individual_rolls = dice.roll_keeping_individual(modifier)
        except DiceStringFormatError:
            context = {
                "game": self.game,
                "show_modal": True,
                "error": f"Invalid dice notation: {dice_notation}",
                "dice_types": [
                    {"value": 4, "label": "d4", "color": "#e74c3c"},
                    {"value": 6, "label": "d6", "color": "#3498db"},
                    {"value": 8, "label": "d8", "color": "#2ecc71"},
                    {"value": 10, "label": "d10", "color": "#e67e22"},
                    {"value": 12, "label": "d12", "color": "#9b59b6"},
                    {"value": 20, "label": "d20", "color": "#f1c40f"},
                ],
            }
            html = render_to_string("game/partials/dice_roller_modal.html", context)
            return HttpResponse(html)

        # Create the event
        DiceRollService.create_dice_roll(
            game=self.game,
            user=request.user,
            dice_notation=dice_notation,
            dice_type=dice_type,
            num_dice=num_dice,
            modifier=modifier,
            individual_rolls=individual_rolls,
            total=total,
            roll_purpose=roll_purpose,
        )

        # Determine color for dice type
        dice_colors = {
            4: "#e74c3c",
            6: "#3498db",
            8: "#2ecc71",
            10: "#e67e22",
            12: "#9b59b6",
            20: "#f1c40f",
        }
        dice_color = dice_colors.get(dice_type, "#f1c40f")

        # Build result context
        context = {
            "game": self.game,
            "show_modal": True,
            "roll_result": True,
            "dice_notation": dice_notation,
            "dice_type": dice_type,
            "num_dice": num_dice,
            "modifier": modifier,
            "individual_rolls": individual_rolls,
            "total": total,
            "roll_purpose": roll_purpose,
            "dice_color": dice_color,
            "animate": True,
            "dice_types": [
                {"value": 4, "label": "d4", "color": "#e74c3c"},
                {"value": 6, "label": "d6", "color": "#3498db"},
                {"value": 8, "label": "d8", "color": "#2ecc71"},
                {"value": 10, "label": "d10", "color": "#e67e22"},
                {"value": 12, "label": "d12", "color": "#9b59b6"},
                {"value": 20, "label": "d20", "color": "#f1c40f"},
            ],
        }

        html = render_to_string("game/partials/dice_roller_modal.html", context)
        return HttpResponse(html)


class QuickRollView(UserPassesTestMixin, GameContextMixin, View):
    """
    View for quick dice rolls from stat blocks and other UI elements.

    Accepts a dice expression string (e.g., "1d20+5") and returns a
    small HTML fragment showing the roll result.
    """

    def test_func(self) -> bool:
        """Verify user is a participant in the game."""
        return self.is_user_master() or self.is_user_player()

    def post(self, request, *args, **kwargs):
        """Process a quick dice roll and return result fragment."""
        dice_expr = request.POST.get("dice", "").strip()
        label = request.POST.get("label", "").strip()

        # Parse the dice expression
        match = DICE_EXPR_REGEX.match(dice_expr)
        if not match:
            return HttpResponse(
                render_to_string(
                    "game/partials/quick_roll_result.html",
                    {"error": f"Invalid dice: {dice_expr}", "game": self.game},
                )
            )

        num_dice = int(match.group(1)) if match.group(1) else 1
        dice_type = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0

        # Clamp values for safety
        num_dice = max(1, min(20, num_dice))
        modifier = max(-50, min(50, modifier))

        # Build dice notation (without modifier for DiceString)
        dice_notation = f"{num_dice}d{dice_type}"

        try:
            dice = DiceString(dice_notation)
            total, individual_rolls = dice.roll_keeping_individual(modifier)
        except DiceStringFormatError:
            return HttpResponse(
                render_to_string(
                    "game/partials/quick_roll_result.html",
                    {"error": f"Invalid dice: {dice_expr}", "game": self.game},
                )
            )

        # Create the event (broadcasts via WebSocket)
        DiceRollService.create_dice_roll(
            game=self.game,
            user=request.user,
            dice_notation=dice_notation,
            dice_type=dice_type,
            num_dice=num_dice,
            modifier=modifier,
            individual_rolls=individual_rolls,
            total=total,
            roll_purpose=label,
        )

        # Determine color for dice type
        dice_colors = {
            4: "#e74c3c",
            6: "#3498db",
            8: "#2ecc71",
            10: "#e67e22",
            12: "#9b59b6",
            20: "#f1c40f",
        }
        dice_color = dice_colors.get(dice_type, "#f1c40f")

        context = {
            "game": self.game,
            "dice_expr": dice_expr,
            "label": label,
            "individual_rolls": individual_rolls,
            "modifier": modifier,
            "total": total,
            "dice_color": dice_color,
            "is_d20": dice_type == 20,
            "is_nat_20": dice_type == 20
            and num_dice == 1
            and individual_rolls[0] == 20,
            "is_nat_1": dice_type == 20 and num_dice == 1 and individual_rolls[0] == 1,
        }

        html = render_to_string("game/partials/quick_roll_result.html", context)
        return HttpResponse(html)
