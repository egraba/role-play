import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import View

from ..constants.abilities import AbilityName
from ..models.character import Character
from ..models.skills import Skill


class SkillsPanelMixin:
    """Mixin for skills panel views."""

    def get_character(self, pk: int) -> Character:
        return get_object_or_404(Character, pk=pk)

    def get_skills_context(
        self, character: Character, ability_filter: str | None = None
    ):
        """Build skills context data with optional ability filter."""
        # Get all skills
        all_skills = Skill.objects.all().select_related("ability_type")
        character_skill_names = set(character.skills.values_list("name", flat=True))

        # Build ability modifier lookup
        ability_modifiers = {}
        for ability in character.abilities.all().select_related("ability_type"):
            ability_modifiers[ability.ability_type.name] = ability.modifier

        # Build skills list
        skills = []
        for skill in all_skills:
            ability_code = skill.ability_type.name

            # Apply filter if specified
            if ability_filter and ability_code != ability_filter:
                continue

            is_proficient = skill.name in character_skill_names
            ability_mod = ability_modifiers.get(ability_code, 0)
            modifier = ability_mod + (
                character.proficiency_bonus if is_proficient else 0
            )

            skills.append(
                {
                    "name": skill.get_name_display(),
                    "ability": ability_code,
                    "ability_modifier": ability_mod,
                    "proficient": is_proficient,
                    "modifier": modifier,
                }
            )

        # Sort skills alphabetically
        skills.sort(key=lambda x: x["name"])

        # Build ability types for filter buttons
        ability_types = [
            {"code": code, "name": name}
            for code, name in AbilityName.choices
            if code != "CON"  # No skills use Constitution
        ]

        return {
            "character": character,
            "skills": skills,
            "ability_filter": ability_filter,
            "ability_types": ability_types,
        }


class SkillsPanelView(LoginRequiredMixin, SkillsPanelMixin, View):
    """Get the skills panel, optionally filtered by ability."""

    def get(self, request, pk: int) -> HttpResponse:
        character = self.get_character(pk)
        ability_filter = request.GET.get("ability")

        # Validate filter
        valid_abilities = {code for code, _ in AbilityName.choices}
        if ability_filter and ability_filter not in valid_abilities:
            ability_filter = None

        context = self.get_skills_context(character, ability_filter)
        html = render_to_string(
            "character/partials/skills_panel.html",
            context,
            request=request,
        )
        return HttpResponse(html)


class SkillRollView(LoginRequiredMixin, SkillsPanelMixin, View):
    """Roll a skill check for a character."""

    def post(self, request, pk: int) -> HttpResponse:
        self.get_character(pk)  # Validate character exists
        skill_name = request.POST.get("skill", "")
        try:
            modifier = int(request.POST.get("modifier", 0))
        except (TypeError, ValueError):
            modifier = 0

        # Roll d20
        d20_roll = random.randint(1, 20)
        total = d20_roll + modifier

        # Determine if natural 20 or natural 1
        is_nat20 = d20_roll == 20
        is_nat1 = d20_roll == 1

        # Build result class
        result_class = ""
        if is_nat20:
            result_class = "nat20"
        elif is_nat1:
            result_class = "nat1"

        # Build breakdown string
        modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
        breakdown = f"d20({d20_roll}) {modifier_str}"

        html = f"""
        <div class="roll-result-content">
            <div class="roll-result-skill">{skill_name} Check</div>
            <div class="roll-result-total {result_class}">{total}</div>
            <div class="roll-result-breakdown">{breakdown}</div>
        </div>
        """
        return HttpResponse(html)
