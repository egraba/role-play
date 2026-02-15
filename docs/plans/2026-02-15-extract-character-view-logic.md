# Extract Business Logic from Character Views — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Move domain logic from `character/views/spells.py` and `character/views/character.py` into `character/services.py`, making views thin HTTP orchestrators.

**Architecture:** Create `character/services.py` with three service classes (`SpellsPanelService`, `CharacterSheetService`, `CharacterCreationService`) following the pattern in `game/services.py`. Views delegate to services for business logic, keeping only HTTP parsing and template rendering.

**Tech Stack:** Python 3.14, Django 6.0, pytest, factory_boy

---

### Task 1: Create SpellsPanelService with get_spells_panel_data

**Files:**
- Create: `character/services.py`
- Test: `character/tests/test_services.py`

**Step 1: Write the failing test**

Create `character/tests/test_services.py`:

```python
import pytest

from character.services import SpellsPanelService
from magic.models.spells import Concentration

from .factories import (
    CharacterFactory,
    CharacterSpellSlotFactory,
    SpellFactory,
    SpellPreparationFactory,
    SpellSettingsFactory,
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def spells_character():
    char = CharacterFactory()
    CharacterSpellSlotFactory(character=char, slot_level=1, total=4, used=1)
    CharacterSpellSlotFactory(character=char, slot_level=2, total=3, used=0)
    CharacterSpellSlotFactory(character=char, slot_level=3, total=2, used=2)

    fireball = SpellSettingsFactory(name="Fireball", level=3, school="evocation", concentration=False)
    shield = SpellSettingsFactory(name="Shield", level=1, school="abjuration", concentration=False)
    hold_person = SpellSettingsFactory(name="Hold Person", level=2, school="enchantment", concentration=True)
    fire_bolt = SpellSettingsFactory(name="Fire Bolt", level=0, school="evocation", concentration=False)

    SpellPreparationFactory(character=char, settings=fireball)
    SpellPreparationFactory(character=char, settings=shield, always_prepared=True)
    SpellFactory(character=char, settings=hold_person)
    SpellFactory(character=char, settings=fire_bolt)

    return char


class TestSpellsPanelServiceGetData:
    def test_returns_spell_slots(self, spells_character):
        data = SpellsPanelService.get_spells_panel_data(spells_character)
        assert len(data["spell_slots"]) == 3
        assert data["spell_slots"][0]["level"] == 1
        assert data["spell_slots"][0]["total"] == 4
        assert data["spell_slots"][0]["remaining"] == 3

    def test_returns_prepared_spells(self, spells_character):
        data = SpellsPanelService.get_spells_panel_data(spells_character)
        assert data["has_prepared"] is True
        prepared_names = {s.settings.name for s in data["prepared_spells"]}
        assert "Fireball" in prepared_names
        assert "Shield" in prepared_names

    def test_returns_known_spells(self, spells_character):
        data = SpellsPanelService.get_spells_panel_data(spells_character)
        assert data["has_known"] is True
        known_names = {s.settings.name for s in data["known_spells"]}
        assert "Hold Person" in known_names
        assert "Fire Bolt" in known_names

    def test_groups_spells_by_level(self, spells_character):
        data = SpellsPanelService.get_spells_panel_data(spells_character)
        assert 3 in data["prepared_by_level"]
        assert 1 in data["prepared_by_level"]

    def test_filter_by_level(self, spells_character):
        data = SpellsPanelService.get_spells_panel_data(spells_character, level_filter=3)
        prepared_names = {s.settings.name for s in data["prepared_spells"]}
        assert "Fireball" in prepared_names
        assert "Shield" not in prepared_names

    def test_filter_by_school(self, spells_character):
        data = SpellsPanelService.get_spells_panel_data(spells_character, school_filter="evocation")
        prepared_names = {s.settings.name for s in data["prepared_spells"]}
        assert "Fireball" in prepared_names
        assert "Shield" not in prepared_names

    def test_filter_by_concentration(self, spells_character):
        data = SpellsPanelService.get_spells_panel_data(spells_character, concentration_filter=True)
        known_names = {s.settings.name for s in data["known_spells"]}
        assert "Hold Person" in known_names
        assert "Fire Bolt" not in known_names

    def test_filter_by_search(self, spells_character):
        data = SpellsPanelService.get_spells_panel_data(spells_character, search_query="fire")
        prepared_names = {s.settings.name for s in data["prepared_spells"]}
        known_names = {s.settings.name for s in data["known_spells"]}
        assert "Fireball" in prepared_names
        assert "Fire Bolt" in known_names
        assert "Shield" not in prepared_names

    def test_returns_quick_cast_cantrips(self, spells_character):
        data = SpellsPanelService.get_spells_panel_data(spells_character)
        cantrip_names = {qc["spell"].settings.name for qc in data["quick_cast_spells"] if qc["can_cast"]}
        assert "Fire Bolt" in cantrip_names

    def test_returns_active_concentration(self, spells_character):
        spell = SpellSettingsFactory(name="Fly", concentration=True)
        Concentration.start_concentration(spells_character, spell)
        data = SpellsPanelService.get_spells_panel_data(spells_character)
        assert data["active_concentration"] is not None

    def test_returns_pact_magic_when_present(self):
        from .factories import WarlockSpellSlotFactory
        char = CharacterFactory()
        WarlockSpellSlotFactory(character=char, slot_level=1, total=1, used=0)
        data = SpellsPanelService.get_spells_panel_data(char)
        assert data["pact_magic"] is not None
        assert data["pact_magic"]["total"] == 1
```

**Step 2: Run test to verify it fails**

Run: `doppler run -- uv run pytest character/tests/test_services.py -v`
Expected: FAIL with `ImportError: cannot import name 'SpellsPanelService' from 'character.services'`

**Step 3: Write minimal implementation**

Create `character/services.py` with `SpellsPanelService.get_spells_panel_data()` — this is a direct extraction of `SpellsPanelMixin.get_spells_context()` from `character/views/spells.py:19-198`:

```python
from __future__ import annotations

from dataclasses import dataclass

from magic.constants.spells import SpellLevel, SpellSchool
from magic.models.spells import Concentration

from .models.character import Character


@dataclass
class SpellCastResult:
    """Result of a spell cast attempt."""

    success: bool
    message: str
    spell_name: str | None = None
    cast_level: int | None = None


class SpellsPanelService:
    """Query and command service for spell-related operations."""

    @staticmethod
    def get_spells_panel_data(
        character: Character,
        *,
        level_filter: int | None = None,
        school_filter: str | None = None,
        concentration_filter: bool | None = None,
        search_query: str | None = None,
    ) -> dict:
        """Build spells panel context data with optional filters.

        This is a pure data-building method with no HTTP dependencies.
        """
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

                if level_filter is not None and settings.level != level_filter:
                    continue
                if school_filter and settings.school != school_filter:
                    continue
                if concentration_filter is not None:
                    if concentration_filter and not settings.concentration:
                        continue
                    if not concentration_filter and settings.concentration:
                        continue
                if search_query:
                    if search_query.lower() not in settings.name.lower():
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
        for spell in prepared_spells:
            if spell.settings.level == 0:
                quick_cast_spells.append(
                    {"spell": spell, "type": "prepared", "can_cast": True}
                )
        for spell in known_spells:
            if spell.settings.level == 0:
                quick_cast_spells.append(
                    {"spell": spell, "type": "known", "can_cast": True}
                )

        first_level_count = 0
        for spell in prepared_spells:
            if spell.settings.level == 1 and first_level_count < 3:
                slot = character.spell_slots.filter(slot_level=1).first()
                can_cast = slot and slot.remaining > 0
                quick_cast_spells.append(
                    {"spell": spell, "type": "prepared", "can_cast": can_cast}
                )
                first_level_count += 1
        for spell in known_spells:
            if spell.settings.level == 1 and first_level_count < 3:
                slot = character.spell_slots.filter(slot_level=1).first()
                can_cast = slot and slot.remaining > 0
                quick_cast_spells.append(
                    {"spell": spell, "type": "known", "can_cast": can_cast}
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
```

**Step 4: Run test to verify it passes**

Run: `doppler run -- uv run pytest character/tests/test_services.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add character/services.py character/tests/test_services.py
git commit -m "feat: add SpellsPanelService.get_spells_panel_data"
```

---

### Task 2: Add SpellsPanelService.cast_spell and restore_all_slots

**Files:**
- Modify: `character/services.py`
- Modify: `character/tests/test_services.py`

**Step 1: Write the failing tests**

Append to `character/tests/test_services.py`:

```python
class TestSpellsPanelServiceCastSpell:
    @pytest.fixture
    def cast_character(self):
        char = CharacterFactory()
        CharacterSpellSlotFactory(character=char, slot_level=1, total=4, used=0)
        CharacterSpellSlotFactory(character=char, slot_level=2, total=3, used=0)
        shield = SpellSettingsFactory(name="Shield", level=1, school="abjuration", concentration=False)
        SpellPreparationFactory(character=char, settings=shield)
        fire_bolt = SpellSettingsFactory(name="Fire Bolt", level=0, school="evocation", concentration=False)
        SpellFactory(character=char, settings=fire_bolt)
        hold_person = SpellSettingsFactory(name="Hold Person", level=2, school="enchantment", concentration=True)
        SpellFactory(character=char, settings=hold_person)
        return char

    def test_cast_cantrip_succeeds(self, cast_character):
        result = SpellsPanelService.cast_spell(cast_character, "Fire Bolt", 0)
        assert result.success is True
        assert "Fire Bolt" in result.message

    def test_cast_cantrip_does_not_use_slot(self, cast_character):
        SpellsPanelService.cast_spell(cast_character, "Fire Bolt", 0)
        slot = cast_character.spell_slots.get(slot_level=1)
        assert slot.used == 0

    def test_cast_leveled_spell_uses_slot(self, cast_character):
        result = SpellsPanelService.cast_spell(cast_character, "Shield", 1)
        assert result.success is True
        slot = cast_character.spell_slots.get(slot_level=1)
        assert slot.used == 1

    def test_cast_concentration_spell_starts_concentration(self, cast_character):
        result = SpellsPanelService.cast_spell(cast_character, "Hold Person", 2)
        assert result.success is True
        assert Concentration.objects.filter(character=cast_character).exists()

    def test_cast_spell_no_slots_remaining(self, cast_character):
        slot = cast_character.spell_slots.get(slot_level=1)
        slot.used = slot.total
        slot.save()
        result = SpellsPanelService.cast_spell(cast_character, "Shield", 1)
        assert result.success is False
        assert "No level 1 slots remaining" in result.message

    def test_cast_unknown_spell_fails(self, cast_character):
        result = SpellsPanelService.cast_spell(cast_character, "Nonexistent", 1)
        assert result.success is False
        assert "Spell not found" in result.message


class TestSpellsPanelServiceRestoreAllSlots:
    def test_restores_all_spell_slots(self):
        char = CharacterFactory()
        CharacterSpellSlotFactory(character=char, slot_level=1, total=4, used=3)
        CharacterSpellSlotFactory(character=char, slot_level=2, total=3, used=2)

        SpellsPanelService.restore_all_slots(char)

        for slot in char.spell_slots.all():
            slot.refresh_from_db()
            assert slot.used == 0

    def test_restores_pact_magic(self):
        from .factories import WarlockSpellSlotFactory
        char = CharacterFactory()
        WarlockSpellSlotFactory(character=char, slot_level=1, total=1, used=1)

        SpellsPanelService.restore_all_slots(char)

        char.pact_magic.refresh_from_db()
        assert char.pact_magic.used == 0
```

**Step 2: Run test to verify it fails**

Run: `doppler run -- uv run pytest character/tests/test_services.py::TestSpellsPanelServiceCastSpell -v`
Expected: FAIL with `AttributeError: type object 'SpellsPanelService' has no attribute 'cast_spell'`

**Step 3: Write minimal implementation**

Add to `SpellsPanelService` in `character/services.py`:

```python
    @staticmethod
    def cast_spell(
        character: Character,
        spell_name: str,
        cast_level: int,
    ) -> SpellCastResult:
        """Cast a spell, consuming a slot if needed.

        Finds the spell in prepared/known lists, validates slot availability,
        consumes the slot, and starts concentration if needed.
        """
        # Find the spell settings
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

        if not spell_settings:
            return SpellCastResult(success=False, message="Spell not found!")

        # Cantrips don't use slots
        if spell_settings.level == 0:
            return SpellCastResult(
                success=True,
                message=f"Cast {spell_settings.name}!",
                spell_name=spell_settings.name,
                cast_level=0,
            )

        # Try to use a slot
        slot = character.spell_slots.filter(slot_level=cast_level).first()
        if not slot or not slot.use_slot():
            return SpellCastResult(
                success=False,
                message=f"No level {cast_level} slots remaining!",
            )

        # Handle concentration
        if spell_settings.concentration:
            Concentration.start_concentration(character, spell_settings)

        return SpellCastResult(
            success=True,
            message=f"Cast {spell_settings.name} at level {cast_level}!",
            spell_name=spell_settings.name,
            cast_level=cast_level,
        )

    @staticmethod
    def restore_all_slots(character: Character) -> None:
        """Restore all spell slots and pact magic (long rest)."""
        for slot in character.spell_slots.all():
            slot.restore_all()

        if hasattr(character, "pact_magic"):
            character.pact_magic.restore_all()
```

**Step 4: Run test to verify it passes**

Run: `doppler run -- uv run pytest character/tests/test_services.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add character/services.py character/tests/test_services.py
git commit -m "feat: add SpellsPanelService.cast_spell and restore_all_slots"
```

---

### Task 3: Wire spells views to SpellsPanelService

**Files:**
- Modify: `character/views/spells.py`

**Step 1: Rewrite `character/views/spells.py` to delegate to service**

Replace the `SpellsPanelMixin.get_spells_context()` body, `CastSpellView.post()` body, and `RestoreAllSlotsView.post()` body with service calls. The mixin's `get_spells_context` becomes a thin wrapper:

```python
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
```

**Step 2: Run existing view tests to verify no regressions**

Run: `doppler run -- uv run pytest character/tests/views/test_spells.py -v`
Expected: All 36 tests PASS (same results as before the change)

**Step 3: Run full service + view test suite**

Run: `doppler run -- uv run pytest character/tests/test_services.py character/tests/views/test_spells.py -v`
Expected: All PASS

**Step 4: Commit**

```bash
git add character/views/spells.py
git commit -m "refactor: wire spells views to SpellsPanelService"
```

---

### Task 4: Add CharacterSheetService.get_character_sheet_data

**Files:**
- Modify: `character/services.py`
- Modify: `character/tests/test_services.py`

**Step 1: Write the failing tests**

Append to `character/tests/test_services.py`:

```python
from character.services import CharacterSheetService
from .factories import (
    CharacterClassFactory,
    CharacterFeatFactory,
    CharacterFeatureFactory,
    ClassFactory,
    ClassFeatureFactory,
    WeaponFactory,
    WeponSettingsFactory,
)


class TestCharacterSheetServiceGetData:
    def test_returns_abilities(self):
        char = CharacterFactory()
        data = CharacterSheetService.get_character_sheet_data(char)
        assert len(data["abilities"]) == 6
        ability_names = {a["abbreviation"] for a in data["abilities"]}
        assert ability_names == {"STR", "DEX", "CON", "INT", "WIS", "CHA"}

    def test_ability_has_required_fields(self):
        char = CharacterFactory()
        data = CharacterSheetService.get_character_sheet_data(char)
        for ability in data["abilities"]:
            assert "name" in ability
            assert "abbreviation" in ability
            assert "score" in ability
            assert "modifier" in ability

    def test_returns_skills(self):
        char = CharacterFactory()
        data = CharacterSheetService.get_character_sheet_data(char)
        assert len(data["skills"]) > 0
        for skill in data["skills"]:
            assert "name" in skill
            assert "ability" in skill
            assert "proficient" in skill
            assert "modifier" in skill

    def test_returns_saving_throws(self):
        char = CharacterFactory()
        data = CharacterSheetService.get_character_sheet_data(char)
        assert len(data["saving_throws"]) == 6
        for save in data["saving_throws"]:
            assert "name" in save
            assert "proficient" in save
            assert "modifier" in save

    def test_returns_attacks_for_character_with_weapon(self):
        from equipment.models.equipment import Weapon, WeaponSettings
        from equipment.constants.equipment import WeaponName
        char = CharacterFactory()
        settings = WeaponSettings.objects.get(name=WeaponName.LONGSWORD)
        Weapon.objects.create(settings=settings, inventory=char.inventory)
        data = CharacterSheetService.get_character_sheet_data(char)
        assert len(data["attacks"]) == 1
        assert "bonus" in data["attacks"][0]
        assert "damage" in data["attacks"][0]

    def test_returns_empty_attacks_without_weapons(self):
        char = CharacterFactory()
        data = CharacterSheetService.get_character_sheet_data(char)
        assert data["attacks"] == []

    def test_returns_racial_traits(self):
        char = CharacterFactory()
        data = CharacterSheetService.get_character_sheet_data(char)
        assert isinstance(data["racial_traits"], list)

    def test_returns_class_features(self):
        char = CharacterFactory()
        data = CharacterSheetService.get_character_sheet_data(char)
        assert isinstance(data["class_features"], list)

    def test_returns_feats(self):
        char = CharacterFactory()
        data = CharacterSheetService.get_character_sheet_data(char)
        assert isinstance(data["feats"], list)
```

**Step 2: Run test to verify it fails**

Run: `doppler run -- uv run pytest character/tests/test_services.py::TestCharacterSheetServiceGetData -v`
Expected: FAIL with `ImportError: cannot import name 'CharacterSheetService'`

**Step 3: Write minimal implementation**

Add to `character/services.py` — direct extraction of `CharacterDetailView.get_context_data()` lines 41-180:

```python
class CharacterSheetService:
    """Query service for character detail page data."""

    @staticmethod
    def get_character_sheet_data(character: Character) -> dict:
        """Build character sheet display data.

        Returns dict with: abilities, skills, saving_throws, attacks,
        racial_traits, class_features, feats, inventory, spells_by_level,
        spell_slots.
        """
        from .models.skills import Skill

        data: dict = {}

        # Inventory
        data["inventory"] = character.inventory

        # Abilities with abbreviations for display
        abilities = []
        for ability in character.abilities.all().select_related("ability_type"):
            abilities.append(
                {
                    "name": ability.ability_type.get_name_display(),
                    "abbreviation": ability.ability_type.name,
                    "score": ability.score,
                    "modifier": ability.modifier,
                }
            )
        data["abilities"] = abilities

        # Skills with proficiency status and modifiers
        all_skills = Skill.objects.all().select_related("ability_type")
        character_skill_names = set(character.skills.values_list("name", flat=True))
        ability_modifiers = {a["abbreviation"]: a["modifier"] for a in abilities}

        skills = []
        for skill in all_skills:
            is_proficient = skill.name in character_skill_names
            ability_mod = ability_modifiers.get(skill.ability_type.name, 0)
            modifier = ability_mod + (
                character.proficiency_bonus if is_proficient else 0
            )
            skills.append(
                {
                    "name": skill.get_name_display(),
                    "ability": skill.ability_type.name,
                    "proficient": is_proficient,
                    "modifier": modifier,
                }
            )
        data["skills"] = skills

        # Saving throws with proficiency and modifiers
        saving_throw_proficiencies = set(
            character.savingthrowproficiency_set.values_list(
                "ability_type__name", flat=True
            )
        )
        saving_throws = []
        for ability in abilities:
            is_proficient = ability["abbreviation"] in saving_throw_proficiencies
            modifier = ability["modifier"] + (
                character.proficiency_bonus if is_proficient else 0
            )
            saving_throws.append(
                {
                    "name": ability["abbreviation"],
                    "proficient": is_proficient,
                    "modifier": modifier,
                }
            )
        data["saving_throws"] = saving_throws

        # Attacks from equipped weapons
        attacks = []
        if character.inventory:
            str_mod = ability_modifiers.get("STR", 0)
            dex_mod = ability_modifiers.get("DEX", 0)
            for weapon in character.inventory.weapon_set.select_related(
                "settings"
            ).all():
                settings = weapon.settings
                is_ranged = settings.weapon_type in ("SR", "MR")
                is_finesse = (
                    settings.properties and "finesse" in settings.properties.lower()
                )
                if is_finesse:
                    attack_mod = max(str_mod, dex_mod)
                elif is_ranged:
                    attack_mod = dex_mod
                else:
                    attack_mod = str_mod
                attack_bonus = attack_mod + character.proficiency_bonus
                damage_dice = settings.damage or "1d4"
                damage = f"{damage_dice}+{attack_mod}" if attack_mod else damage_dice
                attacks.append(
                    {
                        "name": str(weapon),
                        "bonus": attack_bonus,
                        "damage": damage,
                    }
                )
        data["attacks"] = attacks

        # Species/Racial traits
        racial_traits = []
        if character.species:
            for trait in character.species.traits.all():
                racial_traits.append(
                    {
                        "name": trait.get_name_display(),
                        "description": trait.description,
                    }
                )
        data["racial_traits"] = racial_traits

        # Class features
        class_features = []
        for char_feature in character.class_features.all().select_related(
            "class_feature"
        ):
            class_features.append(
                {
                    "name": char_feature.class_feature.name,
                    "description": char_feature.class_feature.description,
                    "level": char_feature.level_gained,
                }
            )
        data["class_features"] = class_features

        # Feats
        feats = []
        for char_feat in character.character_feats.all().select_related("feat"):
            feats.append(
                {
                    "name": char_feat.feat.get_name_display(),
                    "description": char_feat.feat.description,
                }
            )
        data["feats"] = feats

        # Spells (placeholder)
        data["spells_by_level"] = {}
        data["spell_slots"] = []

        return data
```

**Step 4: Run tests**

Run: `doppler run -- uv run pytest character/tests/test_services.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add character/services.py character/tests/test_services.py
git commit -m "feat: add CharacterSheetService.get_character_sheet_data"
```

---

### Task 5: Wire CharacterDetailView to CharacterSheetService

**Files:**
- Modify: `character/views/character.py`

**Step 1: Replace `get_context_data()` body with service call**

In `character/views/character.py`, change `CharacterDetailView.get_context_data()` to:

```python
class CharacterDetailView(LoginRequiredMixin, DetailView):
    model = Character
    template_name = "character/character.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character = self.object
        context.update(CharacterSheetService.get_character_sheet_data(character))
        return context
```

Add the import at the top of the file:
```python
from ..services import CharacterSheetService
```

**Step 2: Run existing view tests**

Run: `doppler run -- uv run pytest character/tests/views/test_character.py::TestCharacterDetailView character/tests/views/test_character.py::TestCharacterDetailViewWithWeapons character/tests/views/test_character.py::TestCharacterDetailViewWithClassFeatures character/tests/views/test_character.py::TestCharacterDetailViewWithFeats character/tests/views/test_character.py::TestCharacterDetailViewWithSpeciesTraits -v`
Expected: All PASS

**Step 3: Commit**

```bash
git add character/views/character.py
git commit -m "refactor: wire CharacterDetailView to CharacterSheetService"
```

---

### Task 6: Add CharacterCreationService.create_character

**Files:**
- Modify: `character/services.py`
- Modify: `character/tests/test_services.py`

**Step 1: Write the failing test**

Append to `character/tests/test_services.py`:

```python
from character.constants.classes import ClassName
from character.models.classes import Class
from character.services import CharacterCreationService
from equipment.constants.equipment import ArmorName, GearName, ToolName, WeaponName
from user.tests.factories import UserFactory


class TestCharacterCreationService:
    def test_creates_character_with_name(self):
        user = UserFactory()
        klass = Class.objects.get(name=ClassName.FIGHTER)
        character = CharacterCreationService.create_character(
            user=user,
            name="Test Hero",
            species=SpeciesFactory(),
            klass=klass,
            abilities={
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8,
            },
            background="acolyte",
            skills=[],
            equipment=[],
        )
        assert character.name == "Test Hero"
        assert character.user == user

    def test_creates_character_with_abilities(self):
        user = UserFactory()
        klass = Class.objects.get(name=ClassName.FIGHTER)
        character = CharacterCreationService.create_character(
            user=user,
            name="Test Hero",
            species=SpeciesFactory(),
            klass=klass,
            abilities={
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8,
            },
            background="acolyte",
            skills=[],
            equipment=[],
        )
        assert character.abilities.count() == 6

    def test_creates_character_with_inventory(self):
        user = UserFactory()
        klass = Class.objects.get(name=ClassName.FIGHTER)
        character = CharacterCreationService.create_character(
            user=user,
            name="Test Hero",
            species=SpeciesFactory(),
            klass=klass,
            abilities={
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8,
            },
            background="acolyte",
            skills=[],
            equipment=[WeaponName.LONGSWORD],
        )
        assert character.inventory is not None
        assert character.inventory.contains(WeaponName.LONGSWORD)

    def test_creates_rogue_with_class_equipment(self):
        user = UserFactory()
        klass = Class.objects.get(name=ClassName.ROGUE)
        character = CharacterCreationService.create_character(
            user=user,
            name="Test Rogue",
            species=SpeciesFactory(),
            klass=klass,
            abilities={
                "strength": 10,
                "dexterity": 15,
                "constitution": 13,
                "intelligence": 14,
                "wisdom": 12,
                "charisma": 8,
            },
            background="criminal",
            skills=[],
            equipment=[],
        )
        assert character.inventory.contains(ArmorName.LEATHER)
        assert character.inventory.contains(WeaponName.DAGGER, 2)
        assert character.inventory.contains(ToolName.THIEVES_TOOLS)

    def test_creates_wizard_with_spellbook(self):
        user = UserFactory()
        klass = Class.objects.get(name=ClassName.WIZARD)
        character = CharacterCreationService.create_character(
            user=user,
            name="Test Wizard",
            species=SpeciesFactory(),
            klass=klass,
            abilities={
                "strength": 8,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 15,
                "wisdom": 12,
                "charisma": 10,
            },
            background="sage",
            skills=[],
            equipment=[],
        )
        assert character.inventory.contains(GearName.SPELLBOOK)

    def test_handles_multi_equipment_names(self):
        user = UserFactory()
        klass = Class.objects.get(name=ClassName.FIGHTER)
        character = CharacterCreationService.create_character(
            user=user,
            name="Test Hero",
            species=SpeciesFactory(),
            klass=klass,
            abilities={
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8,
            },
            background="acolyte",
            skills=[],
            equipment=[f"{WeaponName.HANDAXE} & {WeaponName.HANDAXE}"],
        )
        assert character.inventory.contains(WeaponName.HANDAXE, 2)
```

**Step 2: Run test to verify it fails**

Run: `doppler run -- uv run pytest character/tests/test_services.py::TestCharacterCreationService -v`
Expected: FAIL with `ImportError: cannot import name 'CharacterCreationService'`

**Step 3: Write minimal implementation**

Add to `character/services.py`:

```python
import re

from .character_attributes_builders import (
    BackgroundBuilder,
    BaseBuilder,
    ClassBuilder,
    DerivedStatsBuilder,
    SpeciesBuilder,
    SpellcastingBuilder,
)
from .constants.classes import ClassName
from equipment.constants.equipment import (
    ArmorName,
    GearName,
    ToolName,
    WeaponName,
)

MULTI_EQUIPMENT_REGEX = r"\S+\s&\s\S+"


class CharacterCreationService:
    """Service for creating characters from wizard form data."""

    @staticmethod
    def create_character(
        user,
        *,
        name: str,
        species,
        klass,
        abilities: dict[str, int],
        background: str,
        skills: list[str],
        equipment: list[str],
    ) -> Character:
        """Create a fully built character.

        Orchestrates the builder pipeline and adds equipment.
        Accepts a plain dict of ability scores instead of requiring a form object.

        Args:
            user: The user who owns the character.
            name: Character name.
            species: Species model instance.
            klass: Class model instance.
            abilities: Dict mapping lowercase ability names to scores
                       (e.g. {"strength": 15, "dexterity": 14, ...}).
            background: Background identifier string.
            skills: List of skill name values to add.
            equipment: List of equipment name strings (supports "X & Y" format).
        """
        character = Character(
            user=user,
            name=name,
            species=species,
            background=background,
        )

        # Create a form-like object for BaseBuilder compatibility
        class _AbilityData:
            def __init__(self, data):
                self.cleaned_data = data

        ability_data = _AbilityData(abilities)

        # Phase 1: Base setup - inventory and ability scores
        BaseBuilder(character, ability_data).build()

        # Phase 2: Species traits
        SpeciesBuilder(character).build()

        # Phase 3: Class - HP, proficiencies, features, wealth
        ClassBuilder(character, klass).build()

        # Phase 4: Skills
        for skill_name in skills:
            if skill_name:
                character.skills.add(skill_name)

        # Phase 5: Background
        BackgroundBuilder(character).build()

        # Phase 6: Derived stats
        DerivedStatsBuilder(character).build()

        # Phase 7: Spellcasting
        SpellcastingBuilder(character, klass).build()

        # Phase 8: Equipment
        inventory = character.inventory
        for equipment_name in equipment:
            if not equipment_name:
                continue
            if re.match(MULTI_EQUIPMENT_REGEX, equipment_name):
                names = equipment_name.split(" & ")
                for eq_name in names:
                    inventory.add(eq_name)
            else:
                inventory.add(equipment_name)

        # Class-specific equipment
        match klass.name:
            case ClassName.CLERIC:
                inventory.add(WeaponName.CROSSBOW_LIGHT)
                inventory.add(GearName.CROSSBOW_BOLTS)
                inventory.add(ArmorName.SHIELD)
            case ClassName.ROGUE:
                inventory.add(WeaponName.SHORTBOW)
                inventory.add(GearName.QUIVER)
                inventory.add(ArmorName.LEATHER)
                inventory.add(WeaponName.DAGGER)
                inventory.add(WeaponName.DAGGER)
                inventory.add(ToolName.THIEVES_TOOLS)
            case ClassName.WIZARD:
                inventory.add(GearName.SPELLBOOK)

        return character
```

**Step 4: Run tests**

Run: `doppler run -- uv run pytest character/tests/test_services.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add character/services.py character/tests/test_services.py
git commit -m "feat: add CharacterCreationService.create_character"
```

---

### Task 7: Wire CharacterCreateView to CharacterCreationService

**Files:**
- Modify: `character/views/character.py`

**Step 1: Replace `done()` method body with service call**

Replace the `done()` method of `CharacterCreateView`:

```python
    def done(self, form_list, **kwargs):
        """Process all forms and create the character."""
        forms_by_type = {type(f).__name__: f for f in form_list}

        species_form = forms_by_type.get("SpeciesSelectForm")
        class_form = forms_by_type.get("ClassSelectForm")
        ability_form = forms_by_type.get("AbilityScoreForm")
        background_form = forms_by_type.get("BackgroundSelectForm")
        skills_form = forms_by_type.get("SkillsSelectForm")
        equipment_form = forms_by_type.get("EquipmentSelectForm")
        review_form = forms_by_type.get("ReviewForm")

        klass = class_form.cleaned_data["klass"]

        # Collect skills
        skills = [
            skills_form.cleaned_data[field]
            for field in skills_form.cleaned_data
            if skills_form.cleaned_data[field]
        ]

        # Collect equipment
        equipment = []
        if equipment_form and hasattr(equipment_form, "cleaned_data"):
            equipment = [
                equipment_form.cleaned_data[field]
                for field in equipment_form.cleaned_data
                if equipment_form.cleaned_data.get(field)
            ]

        character = CharacterCreationService.create_character(
            user=self.request.user,
            name=review_form.cleaned_data["name"],
            species=species_form.cleaned_data["species"],
            klass=klass,
            abilities={
                "strength": ability_form.cleaned_data["strength"],
                "dexterity": ability_form.cleaned_data["dexterity"],
                "constitution": ability_form.cleaned_data["constitution"],
                "intelligence": ability_form.cleaned_data["intelligence"],
                "wisdom": ability_form.cleaned_data["wisdom"],
                "charisma": ability_form.cleaned_data["charisma"],
            },
            background=background_form.cleaned_data["background"],
            skills=skills,
            equipment=equipment,
        )

        return HttpResponseRedirect(character.get_absolute_url())
```

Add the import:
```python
from ..services import CharacterCreationService, CharacterSheetService
```

Also remove these now-unused imports from the top of the file:
- `re` (moved to services)
- `MULTI_EQUIPMENT_REGEX` (moved to services)
- All builder imports (`BackgroundBuilder`, `BaseBuilder`, `ClassBuilder`, etc.)
- `ArmorName`, `GearName`, `ToolName`, `WeaponName`
- `ClassName`

**Step 2: Run existing wizard tests**

Run: `doppler run -- uv run pytest character/tests/views/test_character.py::TestCharacterCreateView -v`
Expected: All PASS

**Step 3: Run full test suite for character app**

Run: `doppler run -- uv run pytest character/ -v`
Expected: All PASS

**Step 4: Commit**

```bash
git add character/views/character.py
git commit -m "refactor: wire CharacterCreateView to CharacterCreationService"
```

---

### Task 8: Run pre-commit and full test suite

**Files:**
- Potentially: `character/services.py`, `character/views/spells.py`, `character/views/character.py` (lint fixes)

**Step 1: Run pre-commit**

Run: `pre-commit run --all-files`
Expected: All hooks pass. Fix any issues.

**Step 2: Run full test suite**

Run: `doppler run -- uv run poe test`
Expected: All tests pass.

**Step 3: Run coverage**

Run: `doppler run -- uv run poe test-cov`
Expected: Coverage maintained or improved.

**Step 4: Final commit if any fixes were needed**

```bash
git add -u
git commit -m "chore: lint fixes for service extraction"
```

---

### Task 9: Update documentation

**Files:**
- Modify: `CHANGELOG.md`

**Step 1: Update CHANGELOG.md**

Add under `## Unreleased`:

```markdown
### Changed
- Extracted spell panel business logic from `character/views/spells.py` into `SpellsPanelService` in `character/services.py`
- Extracted character sheet data building from `character/views/character.py` into `CharacterSheetService` in `character/services.py`
- Extracted character creation orchestration from `CharacterCreateView.done()` into `CharacterCreationService` in `character/services.py`
```

**Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: update changelog for character view service extraction"
```
