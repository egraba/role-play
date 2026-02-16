from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from magic.constants.spells import SpellLevel, SpellSchool
from magic.models.spells import Concentration

from .character_attributes_builders import (
    BackgroundBuilder,
    BaseBuilder,
    ClassBuilder,
    DerivedStatsBuilder,
    SpeciesBuilder,
    SpellcastingBuilder,
)
from .constants.classes import ClassName
from .models.character import Character
from equipment.constants.equipment import ArmorName, GearName, ToolName, WeaponName

MULTI_EQUIPMENT_REGEX = r"\S+\s&\s\S+"


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


class CharacterSheetService:
    """Encapsulates business logic for the character detail sheet."""

    @staticmethod
    def get_character_sheet_data(character: Character) -> dict[str, Any]:
        """Build all data needed for the character detail template.

        Computes abilities, skills, saving throws, attacks, racial traits,
        class features, feats, and spell placeholders from the given
        character instance.

        Args:
            character: The character to build sheet data for.

        Returns:
            A dict containing all character sheet display data.
        """
        data: dict[str, Any] = {}

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
        from .models.skills import Skill

        all_skills = Skill.objects.all().select_related("ability_type")
        character_skill_names = set(character.skills.values_list("name", flat=True))

        # Build ability modifier lookup
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
                # Check if weapon is ranged or has finesse property
                is_ranged = settings.weapon_type in ("SR", "MR")
                is_finesse = (
                    settings.properties and "finesse" in settings.properties.lower()
                )
                # Use DEX for finesse/ranged weapons, STR otherwise
                # For finesse, use the higher of STR or DEX
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

        # Spells (placeholder - extend if spellcasting model exists)
        data["spells_by_level"] = {}
        data["spell_slots"] = []

        return data


class CharacterCreationService:
    """Encapsulates the builder orchestration for creating a new character."""

    class _AbilityData:
        """Adapter providing a form-like interface for BaseBuilder compatibility.

        BaseBuilder expects a form object with a ``cleaned_data`` dict
        mapping lowercase ability names to integer scores.
        """

        def __init__(self, data: dict[str, int]) -> None:
            self.cleaned_data = data

    @staticmethod
    def create_character(
        user: Any,
        *,
        name: str,
        species: Any,
        klass: Any,
        abilities: dict[str, int],
        background: str,
        skills: list[str],
        equipment: list[str],
    ) -> Character:
        """Create a fully-built character through the builder pipeline.

        Runs the full character creation pipeline: base setup, species
        traits, class features, skills, background, derived stats,
        spellcasting, equipment, and class-specific default equipment.

        Args:
            user: The user who owns the character.
            name: The character's name.
            species: The species model instance.
            klass: The class model instance.
            abilities: Mapping of lowercase ability names to integer scores.
            background: Background identifier string.
            skills: List of skill names to add.
            equipment: List of equipment name strings (may contain
                ``"Name1 & Name2"`` format for multi-equipment).

        Returns:
            The fully created Character instance.
        """
        # Create character instance
        character = Character(
            user=user,
            name=name,
            species=species,
            background=background,
        )

        # Wrap abilities dict for BaseBuilder compatibility
        ability_data = CharacterCreationService._AbilityData(abilities)

        # Phase 1: Base setup - inventory and ability scores
        BaseBuilder(character, ability_data).build()  # type: ignore[arg-type]

        # Phase 2: Species traits - size, speed, darkvision, languages
        SpeciesBuilder(character).build()

        # Phase 3: Class - HP, proficiencies, features, wealth
        ClassBuilder(character, klass).build()

        # Phase 4: Add skills
        for skill_name in skills:
            if skill_name:
                character.skills.add(skill_name)

        # Phase 5: Background - skill proficiencies, tools, feat, personality
        BackgroundBuilder(character).build()

        # Phase 6: Derived stats (after all modifiers are applied)
        DerivedStatsBuilder(character).build()

        # Phase 7: Spellcasting setup (if class is a spellcaster)
        SpellcastingBuilder(character, klass).build()

        # Phase 8: Add equipment
        inventory = character.inventory
        for equipment_name in equipment:
            if not equipment_name:
                continue
            # If the field is under the form "equipment_name1 & equipment_name2",
            # each equipment must be added separately.
            if re.match(MULTI_EQUIPMENT_REGEX, equipment_name):
                names = equipment_name.split(" & ")
                for item_name in names:
                    inventory.add(item_name)
            else:
                inventory.add(equipment_name)

        # Some equipment is added without selection, depending on character's class.
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
