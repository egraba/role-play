from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View

from utils.dice import DiceString, DiceStringFormatError

from ..services import DiceRollService
from .mixins import GameContextMixin


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
