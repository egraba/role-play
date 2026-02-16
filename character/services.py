from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from magic.constants.spells import SpellLevel, SpellSchool
from magic.models.spells import Concentration

from .models.character import Character


@dataclass
class SpellCastResult:
    success: bool
    message: str
    spell_name: str | None = None
    cast_level: int | None = None


class SpellsPanelService:
    """Encapsulates business logic for the spells panel."""

    @staticmethod
    def cast_spell(
        character: Character,
        spell_name: str,
        cast_level: int,
    ) -> SpellCastResult:
        """Cast a spell, consuming a slot if needed and starting concentration.

        Searches prepared_spells then spells_known for a spell matching
        spell_name. Cantrips (level 0) are cast without consuming a slot.
        Leveled spells consume a slot at cast_level. Concentration spells
        start concentration on the character.

        Args:
            character: The character casting the spell.
            spell_name: The name of the spell to cast.
            cast_level: The level at which to cast the spell.

        Returns:
            A SpellCastResult indicating success/failure and a message.
        """
        # Find the spell in prepared spells first, then known spells
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

        # Try to use a slot at the cast level
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
        """Restore all spell slots and pact magic (long rest).

        Iterates all character spell slots calling restore_all() on each,
        and also restores pact magic if the character has it.

        Args:
            character: The character whose slots to restore.
        """
        for slot in character.spell_slots.all():
            slot.restore_all()

        if hasattr(character, "pact_magic"):
            character.pact_magic.restore_all()

    @staticmethod
    def get_spells_panel_data(
        character: Character,
        *,
        level_filter: int | None = None,
        school_filter: str | None = None,
        concentration_filter: bool | None = None,
        search_query: str | None = None,
    ) -> dict[str, Any]:
        """Build all data needed for the spells panel template.

        Args:
            character: The character whose spells to retrieve.
            level_filter: Optional spell level to filter by.
            school_filter: Optional spell school to filter by.
            concentration_filter: Optional concentration flag to filter by.
            search_query: Optional case-insensitive name substring to filter by.

        Returns:
            A dict containing spell slots, prepared/known spells (flat and
            grouped by level), quick-cast spells, active concentration,
            filter option lists, and the current filter values.
        """
        # -- Spell slots with circle visualization --
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

        # -- Pact magic (Warlock) --
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

        # -- Prepared and known spells --
        prepared_spells = list(
            character.prepared_spells.select_related("settings").all()
        )
        known_spells = list(character.spells_known.select_related("settings").all())

        # -- Filtering --
        def filter_spells(
            spell_list: list,
        ) -> list:
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
                    query_lower = search_query.lower()
                    if query_lower not in settings.name.lower():
                        continue

                filtered.append(spell)
            return filtered

        prepared_spells = filter_spells(prepared_spells)
        known_spells = filter_spells(known_spells)

        # -- Group by level --
        def group_by_level(spell_list: list) -> dict[int, list]:
            grouped: dict[int, list] = {}
            for spell in spell_list:
                level = spell.settings.level
                if level not in grouped:
                    grouped[level] = []
                grouped[level].append(spell)
            return dict(sorted(grouped.items()))

        prepared_by_level = group_by_level(prepared_spells)
        known_by_level = group_by_level(known_spells)

        # -- Active concentration --
        active_concentration = None
        try:
            active_concentration = character.concentration
        except Concentration.DoesNotExist:
            pass

        # -- Quick-cast spells (cantrips + first few 1st-level) --
        quick_cast_spells: list[dict[str, Any]] = []

        # Add all cantrips from prepared and known
        for spell in prepared_spells:
            if spell.settings.level == 0:
                quick_cast_spells.append(
                    {
                        "spell": spell,
                        "type": "prepared",
                        "can_cast": True,
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

        # -- Filter options --
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
