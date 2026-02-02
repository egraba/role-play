import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import View

from ..ability_modifiers import compute_ability_modifier
from ..constants.abilities import AbilityName
from ..models.character import Character
from ..models.species import Species


# Point buy costs per score (D&D 5e standard)
POINT_BUY_COSTS = {
    8: 0,
    9: 1,
    10: 2,
    11: 3,
    12: 4,
    13: 5,
    14: 7,
    15: 9,
}

# Standard array values
STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]

# Total points for point buy
POINT_BUY_TOTAL = 27


def roll_4d6_drop_lowest():
    """Roll 4d6 and drop the lowest die."""
    rolls = [random.randint(1, 6) for _ in range(4)]
    rolls.sort(reverse=True)
    return sum(rolls[:3]), rolls


class AbilityAssignmentModalView(LoginRequiredMixin, View):
    """Display the ability score assignment modal."""

    def get(self, request, pk: int) -> HttpResponse:
        character = get_object_or_404(Character, pk=pk)

        # Get all species for racial bonus selection
        species_list = Species.objects.all()

        # Build ability info
        abilities = []
        for name, label in AbilityName.choices:
            abilities.append(
                {
                    "name": name,
                    "label": label,
                    "score": 8,
                    "modifier": compute_ability_modifier(8),
                    "racial_bonus": 0,
                }
            )

        context = {
            "character": character,
            "show_modal": True,
            "abilities": abilities,
            "species_list": species_list,
            "point_buy_costs": POINT_BUY_COSTS,
            "point_buy_total": POINT_BUY_TOTAL,
            "standard_array": STANDARD_ARRAY,
            "mode": "point_buy",
            "points_remaining": POINT_BUY_TOTAL,
        }
        html = render_to_string(
            "character/partials/ability_assignment_modal.html",
            context,
            request=request,
        )
        return HttpResponse(html)


class AbilityPointBuyView(LoginRequiredMixin, View):
    """Handle point buy ability score changes."""

    def post(self, request, pk: int) -> HttpResponse:
        character = get_object_or_404(Character, pk=pk)
        species_list = Species.objects.all()

        # Parse ability scores from form
        abilities = []
        total_cost = 0

        # Get racial bonuses
        racial_bonuses = {}
        for name, _ in AbilityName.choices:
            bonus_key = f"racial_bonus_{name}"
            try:
                racial_bonuses[name] = int(request.POST.get(bonus_key, 0))
            except (TypeError, ValueError):
                racial_bonuses[name] = 0

        for name, label in AbilityName.choices:
            try:
                score = int(request.POST.get(f"ability_{name}", 8))
                score = max(8, min(15, score))  # Clamp to valid range
            except (TypeError, ValueError):
                score = 8

            cost = POINT_BUY_COSTS.get(score, 0)
            total_cost += cost
            racial_bonus = racial_bonuses.get(name, 0)
            final_score = score + racial_bonus

            abilities.append(
                {
                    "name": name,
                    "label": label,
                    "score": score,
                    "racial_bonus": racial_bonus,
                    "final_score": final_score,
                    "modifier": compute_ability_modifier(final_score),
                    "cost": cost,
                }
            )

        points_remaining = POINT_BUY_TOTAL - total_cost
        is_valid = points_remaining >= 0

        context = {
            "character": character,
            "show_modal": True,
            "abilities": abilities,
            "species_list": species_list,
            "point_buy_costs": POINT_BUY_COSTS,
            "point_buy_total": POINT_BUY_TOTAL,
            "standard_array": STANDARD_ARRAY,
            "mode": "point_buy",
            "points_remaining": points_remaining,
            "points_spent": total_cost,
            "is_valid": is_valid,
            "racial_bonuses": racial_bonuses,
        }
        html = render_to_string(
            "character/partials/ability_assignment_modal.html",
            context,
            request=request,
        )
        return HttpResponse(html)


class AbilityStandardArrayView(LoginRequiredMixin, View):
    """Handle standard array ability score assignment."""

    def post(self, request, pk: int) -> HttpResponse:
        character = get_object_or_404(Character, pk=pk)
        species_list = Species.objects.all()

        # Get racial bonuses
        racial_bonuses = {}
        for name, _ in AbilityName.choices:
            bonus_key = f"racial_bonus_{name}"
            try:
                racial_bonuses[name] = int(request.POST.get(bonus_key, 0))
            except (TypeError, ValueError):
                racial_bonuses[name] = 0

        # Parse assigned scores
        abilities = []
        assigned_values = []

        for name, label in AbilityName.choices:
            try:
                score = int(request.POST.get(f"ability_{name}", 0))
                if score not in STANDARD_ARRAY:
                    score = 0
            except (TypeError, ValueError):
                score = 0

            if score > 0:
                assigned_values.append(score)

            racial_bonus = racial_bonuses.get(name, 0)
            final_score = score + racial_bonus if score > 0 else 0

            abilities.append(
                {
                    "name": name,
                    "label": label,
                    "score": score,
                    "racial_bonus": racial_bonus,
                    "final_score": final_score,
                    "modifier": compute_ability_modifier(final_score)
                    if final_score > 0
                    else None,
                }
            )

        # Check for duplicate assignments
        has_duplicates = len(assigned_values) != len(set(assigned_values))
        unassigned = [v for v in STANDARD_ARRAY if v not in assigned_values]
        is_complete = len(assigned_values) == 6 and not has_duplicates

        context = {
            "character": character,
            "show_modal": True,
            "abilities": abilities,
            "species_list": species_list,
            "point_buy_costs": POINT_BUY_COSTS,
            "point_buy_total": POINT_BUY_TOTAL,
            "standard_array": STANDARD_ARRAY,
            "mode": "standard_array",
            "unassigned_values": unassigned,
            "is_complete": is_complete,
            "has_duplicates": has_duplicates,
            "racial_bonuses": racial_bonuses,
        }
        html = render_to_string(
            "character/partials/ability_assignment_modal.html",
            context,
            request=request,
        )
        return HttpResponse(html)


class AbilityRollView(LoginRequiredMixin, View):
    """Handle rolling for ability scores."""

    def post(self, request, pk: int) -> HttpResponse:
        character = get_object_or_404(Character, pk=pk)
        species_list = Species.objects.all()

        # Get racial bonuses
        racial_bonuses = {}
        for name, _ in AbilityName.choices:
            bonus_key = f"racial_bonus_{name}"
            try:
                racial_bonuses[name] = int(request.POST.get(bonus_key, 0))
            except (TypeError, ValueError):
                racial_bonuses[name] = 0

        # Check if we should reroll or use existing rolls
        action = request.POST.get("action", "roll")

        abilities = []
        rolled_totals = []
        all_dice = []

        if action == "roll" or action == "reroll":
            # Generate new rolls
            for name, label in AbilityName.choices:
                total, dice = roll_4d6_drop_lowest()
                rolled_totals.append(total)
                all_dice.append(dice)

                racial_bonus = racial_bonuses.get(name, 0)
                final_score = total + racial_bonus

                abilities.append(
                    {
                        "name": name,
                        "label": label,
                        "score": total,
                        "dice": dice,
                        "dropped_die": dice[3],  # Lowest die
                        "racial_bonus": racial_bonus,
                        "final_score": final_score,
                        "modifier": compute_ability_modifier(final_score),
                    }
                )
        else:
            # Keep existing rolls from form
            for i, (name, label) in enumerate(AbilityName.choices):
                try:
                    score = int(request.POST.get(f"ability_{name}", 10))
                except (TypeError, ValueError):
                    score = 10

                dice_str = request.POST.get(f"dice_{name}", "")
                dice = [int(d) for d in dice_str.split(",") if d] if dice_str else []

                racial_bonus = racial_bonuses.get(name, 0)
                final_score = score + racial_bonus

                abilities.append(
                    {
                        "name": name,
                        "label": label,
                        "score": score,
                        "dice": dice,
                        "dropped_die": dice[3] if len(dice) > 3 else None,
                        "racial_bonus": racial_bonus,
                        "final_score": final_score,
                        "modifier": compute_ability_modifier(final_score),
                    }
                )

        context = {
            "character": character,
            "show_modal": True,
            "abilities": abilities,
            "species_list": species_list,
            "point_buy_costs": POINT_BUY_COSTS,
            "point_buy_total": POINT_BUY_TOTAL,
            "standard_array": STANDARD_ARRAY,
            "mode": "roll",
            "has_rolled": True,
            "animate_dice": action in ("roll", "reroll"),
            "racial_bonuses": racial_bonuses,
        }
        html = render_to_string(
            "character/partials/ability_assignment_modal.html",
            context,
            request=request,
        )
        return HttpResponse(html)


class AbilitySaveView(LoginRequiredMixin, View):
    """Save the assigned ability scores to the character."""

    def post(self, request, pk: int) -> HttpResponse:
        from ..models.abilities import Ability, AbilityType

        character = get_object_or_404(Character, pk=pk)

        # Clear existing abilities
        character.abilities.all().delete()

        # Get racial bonuses
        racial_bonuses = {}
        for name, _ in AbilityName.choices:
            bonus_key = f"racial_bonus_{name}"
            try:
                racial_bonuses[name] = int(request.POST.get(bonus_key, 0))
            except (TypeError, ValueError):
                racial_bonuses[name] = 0

        # Create new abilities
        for name, label in AbilityName.choices:
            try:
                base_score = int(request.POST.get(f"ability_{name}", 10))
            except (TypeError, ValueError):
                base_score = 10

            racial_bonus = racial_bonuses.get(name, 0)
            final_score = base_score + racial_bonus

            # Ensure score is within valid range
            final_score = max(1, min(30, final_score))

            ability_type = AbilityType.objects.get(name=name)
            ability = Ability.objects.create(
                ability_type=ability_type,
                score=final_score,
            )
            character.abilities.add(ability)

        # Return success state
        abilities = []
        for name, label in AbilityName.choices:
            ability = character.abilities.get(ability_type__name=name)
            abilities.append(
                {
                    "name": name,
                    "label": label,
                    "score": ability.score,
                    "modifier": ability.modifier,
                }
            )

        context = {
            "character": character,
            "show_modal": True,
            "abilities": abilities,
            "save_success": True,
        }
        html = render_to_string(
            "character/partials/ability_assignment_modal.html",
            context,
            request=request,
        )
        return HttpResponse(html)
