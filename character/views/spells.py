from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import View

from magic.constants.spells import SpellLevel, SpellSchool
from magic.models.spells import Concentration

from ..models.character import Character


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
        # Get spell slots with visualization data
        spell_slots = []
        for slot in character.spell_slots.all().order_by("slot_level"):
            if slot.total > 0:
                circles = []
                for i in range(slot.total):
                    circles.append({"filled": i >= slot.used})
                spell_slots.append(
                    {
                        "level": slot.slot_level,
                        "total": slot.total,
                        "used": slot.used,
                        "remaining": slot.remaining,
                        "circles": circles,
                    }
                )

        # Check for pact magic (Warlock)
        pact_magic = None
        if hasattr(character, "pact_magic"):
            pm = character.pact_magic
            circles = []
            for i in range(pm.total):
                circles.append({"filled": i >= pm.used})
            pact_magic = {
                "level": pm.slot_level,
                "total": pm.total,
                "used": pm.used,
                "remaining": pm.remaining,
                "circles": circles,
            }

        # Get prepared spells (for prepared casters)
        prepared_spells = list(
            character.prepared_spells.select_related("settings").all()
        )

        # Get known spells (for spontaneous casters)
        known_spells = list(character.spells_known.select_related("settings").all())

        # Apply filters to both lists
        def filter_spells(spell_list):
            filtered = []
            for spell in spell_list:
                settings = spell.settings

                # Level filter
                if level_filter is not None and settings.level != level_filter:
                    continue

                # School filter
                if school_filter and settings.school != school_filter:
                    continue

                # Concentration filter
                if concentration_filter is not None:
                    if concentration_filter and not settings.concentration:
                        continue
                    if not concentration_filter and settings.concentration:
                        continue

                # Search query
                if search_query:
                    query_lower = search_query.lower()
                    if query_lower not in settings.name.lower():
                        continue

                filtered.append(spell)
            return filtered

        prepared_spells = filter_spells(prepared_spells)
        known_spells = filter_spells(known_spells)

        # Group spells by level
        def group_by_level(spell_list):
            grouped = {}
            for spell in spell_list:
                level = spell.settings.level
                if level not in grouped:
                    grouped[level] = []
                grouped[level].append(spell)
            return dict(sorted(grouped.items()))

        prepared_by_level = group_by_level(prepared_spells)
        known_by_level = group_by_level(known_spells)

        # Get active concentration
        active_concentration = None
        try:
            active_concentration = character.concentration
        except Concentration.DoesNotExist:
            pass

        # Build quick-cast spells (cantrips + frequently used 1st level)
        quick_cast_spells = []

        # Add all cantrips from prepared and known
        for spell in prepared_spells:
            if spell.settings.level == 0:
                quick_cast_spells.append(
                    {
                        "spell": spell,
                        "type": "prepared",
                        "can_cast": True,  # Cantrips always castable
                    }
                )
        for spell in known_spells:
            if spell.settings.level == 0:
                quick_cast_spells.append(
                    {
                        "spell": spell,
                        "type": "known",
                        "can_cast": True,
                    }
                )

        # Add first few 1st-level spells
        first_level_count = 0
        for spell in prepared_spells:
            if spell.settings.level == 1 and first_level_count < 3:
                # Check if slot available
                slot = character.spell_slots.filter(slot_level=1).first()
                can_cast = slot and slot.remaining > 0
                quick_cast_spells.append(
                    {
                        "spell": spell,
                        "type": "prepared",
                        "can_cast": can_cast,
                    }
                )
                first_level_count += 1
        for spell in known_spells:
            if spell.settings.level == 1 and first_level_count < 3:
                slot = character.spell_slots.filter(slot_level=1).first()
                can_cast = slot and slot.remaining > 0
                quick_cast_spells.append(
                    {
                        "spell": spell,
                        "type": "known",
                        "can_cast": can_cast,
                    }
                )
                first_level_count += 1

        # Build filter options
        spell_levels = [
            {"value": level, "label": label} for level, label in SpellLevel.choices
        ]
        spell_schools = [
            {"value": school, "label": label} for school, label in SpellSchool.choices
        ]

        return {
            "character": character,
            "spell_slots": spell_slots,
            "pact_magic": pact_magic,
            "prepared_spells": prepared_spells,
            "known_spells": known_spells,
            "prepared_by_level": prepared_by_level,
            "known_by_level": known_by_level,
            "quick_cast_spells": quick_cast_spells,
            "active_concentration": active_concentration,
            "level_filter": level_filter,
            "school_filter": school_filter,
            "concentration_filter": concentration_filter,
            "search_query": search_query,
            "spell_levels": spell_levels,
            "spell_schools": spell_schools,
            "has_prepared": len(prepared_spells) > 0,
            "has_known": len(known_spells) > 0,
        }


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

        for slot in character.spell_slots.all():
            slot.restore_all()

        # Also restore pact magic if applicable
        if hasattr(character, "pact_magic"):
            character.pact_magic.restore_all()

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

        # Find the spell
        spell_settings = None
        for spell in character.prepared_spells.select_related("settings").all():
            if spell.settings.name == spell_name:
                spell_settings = spell.settings
                break
        if not spell_settings:
            for spell in character.spells_known.select_related("settings").all():
                if spell.settings.name == spell_name:
                    spell_settings = spell.settings
                    break

        result_message = None
        if spell_settings:
            # Cantrips don't use slots
            if spell_settings.level == 0:
                result_message = f"Cast {spell_settings.name}!"
            else:
                # Try to use a slot
                slot = character.spell_slots.filter(slot_level=cast_level).first()
                if slot and slot.use_slot():
                    result_message = (
                        f"Cast {spell_settings.name} at level {cast_level}!"
                    )
                    # Handle concentration
                    if spell_settings.concentration:
                        Concentration.start_concentration(character, spell_settings)
                else:
                    result_message = f"No level {cast_level} slots remaining!"
        else:
            result_message = "Spell not found!"

        context = self.get_spells_context(character)
        context["cast_result"] = result_message
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
