from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import View

from magic.constants.spells import SpellSchool
from magic.models.spells import Concentration

from ..models.character import Character
from ..services import SpellsPanelService


class SpellsPanelMixin:
    """Mixin for spells panel views."""

    def get_character(self, pk: int) -> Character:
        return get_object_or_404(Character, pk=pk)

    def get_spells_context(
        self,
        character: Character,
        level_filter: int | None = None,
        school_filter: str | None = None,
        concentration_filter: bool | None = None,
        search_query: str | None = None,
    ):
        """Build spells context data with optional filters."""
        return SpellsPanelService.get_spells_panel_data(
            character,
            level_filter=level_filter,
            school_filter=school_filter,
            concentration_filter=concentration_filter,
            search_query=search_query,
        )


class SpellsPanelView(LoginRequiredMixin, SpellsPanelMixin, View):
    """Get the spells panel, optionally filtered."""

    def get(self, request, pk: int) -> HttpResponse:
        character = self.get_character(pk)

        # Parse filters from query params
        level_filter = request.GET.get("level")
        if level_filter is not None:
            try:
                level_filter = int(level_filter)
            except (TypeError, ValueError):
                level_filter = None

        school_filter = request.GET.get("school")
        valid_schools = {school for school, _ in SpellSchool.choices}
        if school_filter and school_filter not in valid_schools:
            school_filter = None

        concentration_filter = request.GET.get("concentration")
        if concentration_filter is not None:
            concentration_filter = concentration_filter.lower() == "true"
        else:
            concentration_filter = None

        search_query = request.GET.get("search", "").strip()
        if not search_query:
            search_query = None

        context = self.get_spells_context(
            character,
            level_filter=level_filter,
            school_filter=school_filter,
            concentration_filter=concentration_filter,
            search_query=search_query,
        )
        html = render_to_string(
            "character/partials/spells_panel.html",
            context,
            request=request,
        )
        return HttpResponse(html)


class UseSpellSlotView(LoginRequiredMixin, SpellsPanelMixin, View):
    """Use a spell slot."""

    def post(self, request, pk: int) -> HttpResponse:
        character = self.get_character(pk)

        try:
            slot_level = int(request.POST.get("slot_level", 1))
        except (TypeError, ValueError):
            slot_level = 1

        slot = character.spell_slots.filter(slot_level=slot_level).first()
        if slot:
            slot.use_slot()

        # Return just the spell slots section
        context = self.get_spells_context(character)
        html = render_to_string(
            "character/partials/spells_panel.html",
            context,
            request=request,
        )
        return HttpResponse(html)


class RestoreSpellSlotView(LoginRequiredMixin, SpellsPanelMixin, View):
    """Restore a spell slot."""

    def post(self, request, pk: int) -> HttpResponse:
        character = self.get_character(pk)

        try:
            slot_level = int(request.POST.get("slot_level", 1))
        except (TypeError, ValueError):
            slot_level = 1

        slot = character.spell_slots.filter(slot_level=slot_level).first()
        if slot:
            slot.restore_slot()

        context = self.get_spells_context(character)
        html = render_to_string(
            "character/partials/spells_panel.html",
            context,
            request=request,
        )
        return HttpResponse(html)


class RestoreAllSlotsView(LoginRequiredMixin, SpellsPanelMixin, View):
    """Restore all spell slots (long rest)."""

    def post(self, request, pk: int) -> HttpResponse:
        character = self.get_character(pk)
        SpellsPanelService.restore_all_slots(character)
        context = self.get_spells_context(character)
        html = render_to_string(
            "character/partials/spells_panel.html",
            context,
            request=request,
        )
        return HttpResponse(html)


class CastSpellView(LoginRequiredMixin, SpellsPanelMixin, View):
    """Quick-cast a spell, consuming a slot if needed."""

    def post(self, request, pk: int) -> HttpResponse:
        character = self.get_character(pk)

        spell_name = request.POST.get("spell_name")
        try:
            cast_level = int(request.POST.get("cast_level", 1))
        except (TypeError, ValueError):
            cast_level = 1

        result = SpellsPanelService.cast_spell(character, spell_name, cast_level)
        context = self.get_spells_context(character)
        context["cast_result"] = result.message
        html = render_to_string(
            "character/partials/spells_panel.html",
            context,
            request=request,
        )
        return HttpResponse(html)


class BreakConcentrationView(LoginRequiredMixin, SpellsPanelMixin, View):
    """Break concentration on current spell."""

    def post(self, request, pk: int) -> HttpResponse:
        character = self.get_character(pk)

        try:
            character.concentration.break_concentration()
        except Concentration.DoesNotExist:
            pass

        context = self.get_spells_context(character)
        html = render_to_string(
            "character/partials/spells_panel.html",
            context,
            request=request,
        )
        return HttpResponse(html)


class SpellCardModalView(LoginRequiredMixin, SpellsPanelMixin, View):
    """View for displaying full spell details in a modal."""

    def get(self, request, pk: int, spell_name: str) -> HttpResponse:
        """Show the spell card modal for a specific spell."""
        from magic.models.spells import CharacterSpellSlot, SpellSettings

        character = self.get_character(pk)
        spell = get_object_or_404(SpellSettings, name=spell_name)

        # Get available spell slots for upcasting options
        available_slots = []
        if spell.level > 0:
            slots = CharacterSpellSlot.objects.filter(
                character=character,
                slot_level__gte=spell.level,
                total__gt=0,
            ).order_by("slot_level")
            for slot in slots:
                available_slots.append(
                    {
                        "level": slot.slot_level,
                        "remaining": slot.remaining,
                        "total": slot.total,
                        "available": slot.remaining > 0,
                    }
                )

        context = {
            "character": character,
            "spell": spell,
            "show_modal": True,
            "available_slots": available_slots,
            "is_cantrip": spell.level == 0,
        }
        html = render_to_string(
            "character/partials/spell_card_modal.html",
            context,
            request=request,
        )
        return HttpResponse(html)
