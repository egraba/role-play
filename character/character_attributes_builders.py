import random
from abc import ABC, abstractmethod

from utils.dice import DiceString

from .constants.backgrounds import BACKGROUNDS
from .constants.skills import SkillName
from .forms.character import CharacterCreateForm
from .models.abilities import Ability, AbilityType
from .models.character import Character
from .models.equipment import Inventory, ToolSettings
from .models.feats import CharacterFeat, Feat
from .models.classes import CharacterClass, CharacterFeature, Class
from .models.proficiencies import (
    ArmorProficiency,
    SavingThrowProficiency,
    SkillProficiency,
    ToolProficiency,
    WeaponProficiency,
)
from .models.equipment import ArmorSettings, WeaponSettings
from .models.skills import Skill
from .models.spells import (
    CharacterSpellSlot,
    ClassSpellcasting,
    SpellSlotTable,
    WarlockSpellSlot,
)


class CharacterAttributesBuilder(ABC):
    @abstractmethod
    def build(self) -> None:
        pass


class BaseBuilder(CharacterAttributesBuilder):
    def __init__(self, character: Character, form: CharacterCreateForm) -> None:
        self.character = character
        self.form = form

    def _add_inventory(self) -> None:
        self.character.inventory = Inventory.objects.create()

    def _initialize_ability_scores(self) -> None:
        for ability_type in AbilityType.objects.all():
            ability = Ability.objects.create(
                ability_type=ability_type,
                score=self.form.cleaned_data[ability_type.get_name_display().lower()],
            )
            self.character.abilities.add(ability)

    def build(self) -> None:
        self._add_inventory()
        self.character.save()
        self._initialize_ability_scores()


class SpeciesBuilder(CharacterAttributesBuilder):
    """Apply species traits to a character (D&D 2024 rules)."""

    def __init__(self, character: Character) -> None:
        self.character = character
        self.species = character.species

    def _apply_species_traits(self) -> None:
        """Apply size, speed, darkvision, and languages from species."""
        if not self.species:
            return
        self.character.size = self.species.size
        self.character.speed = self.species.speed
        self.character.darkvision = self.species.darkvision
        # Need to save before setting many-to-many relationships
        self.character.save()
        for language in self.species.languages.all():
            self.character.languages.add(language)

    def build(self) -> None:
        self._apply_species_traits()
        self.character.save()


class ClassBuilder(CharacterAttributesBuilder):
    """Apply class features to a character using the new Class model."""

    def __init__(self, character: Character, klass: Class) -> None:
        self.character = character
        self.klass = klass

    def _create_character_class(self) -> None:
        """Create the CharacterClass junction record."""
        CharacterClass.objects.create(
            character=self.character,
            klass=self.klass,
            level=1,
            is_primary=True,
        )

    def _apply_hit_points(self) -> None:
        """Set hit dice, HP, and HP increase from class."""
        self.character.hit_dice = f"1d{self.klass.hit_die}"
        base_hp = self.klass.hp_first_level
        con_mod = self.character.constitution.modifier
        self.character.hp = 100 + base_hp + con_mod
        self.character.max_hp = self.character.hp
        self.character.hp_increase = self.klass.hp_higher_levels

    def _apply_saving_throw_proficiencies(self) -> None:
        """Grant saving throw proficiencies from class."""
        for ability_type in self.klass.saving_throws.all():
            SavingThrowProficiency.objects.create(
                character=self.character, ability_type=ability_type
            )

    def _apply_armor_proficiencies(self) -> None:
        """Grant armor proficiencies based on class armor type categories."""
        armor_types = self.klass.armor_proficiencies  # e.g., ["LA", "MA", "SH"]
        if not armor_types:
            return
        for armor in ArmorSettings.objects.filter(armor_type__in=armor_types):
            ArmorProficiency.objects.create(character=self.character, armor=armor)

    def _apply_weapon_proficiencies(self) -> None:
        """Grant weapon proficiencies based on class weapon categories.

        Categories are 'simple' (SM, SR) and 'martial' (MM, MR).
        """
        weapon_categories = (
            self.klass.weapon_proficiencies
        )  # e.g., ["simple", "martial"]
        if not weapon_categories:
            return
        # Map category names to weapon type codes
        weapon_types = []
        if "simple" in weapon_categories:
            weapon_types.extend(["SM", "SR"])  # Simple Melee, Simple Ranged
        if "martial" in weapon_categories:
            weapon_types.extend(["MM", "MR"])  # Martial Melee, Martial Ranged
        for weapon in WeaponSettings.objects.filter(weapon_type__in=weapon_types):
            WeaponProficiency.objects.create(character=self.character, weapon=weapon)

    def _add_starting_wealth(self) -> None:
        """Roll and add starting wealth from class."""
        wealth_roll = DiceString(self.klass.starting_wealth_dice).roll()
        self.character.inventory.gp += wealth_roll * 10
        self.character.inventory.save()

    def _apply_class_features(self) -> None:
        """Grant level 1 class features to the character."""
        level_1_features = self.klass.features.filter(level=1)
        for feature in level_1_features:
            CharacterFeature.objects.create(
                character=self.character,
                class_feature=feature,
                source_class=self.klass,
                level_gained=1,
            )

    def build(self) -> None:
        self._create_character_class()
        self._apply_hit_points()
        self._apply_saving_throw_proficiencies()
        self._apply_armor_proficiencies()
        self._apply_weapon_proficiencies()
        self._apply_class_features()
        self._add_starting_wealth()
        self.character.save()


class BackgroundBuilder:
    def __init__(self, character: Character) -> None:
        self.character = character
        self.background = character.background

    def _add_skill_proficiencies(self) -> None:
        skill_proficiencies = BACKGROUNDS[self.background]["skill_proficiencies"]
        for skill in skill_proficiencies:
            SkillProficiency.objects.create(
                character=self.character, skill=Skill.objects.get(name=skill)
            )

    def _add_tool_proficiency(self) -> None:
        """Grant tool proficiency from background."""
        tool_name = BACKGROUNDS[self.background].get("tool_proficiency")
        if tool_name:
            tool = ToolSettings.objects.get(name=tool_name)
            ToolProficiency.objects.create(character=self.character, tool=tool)

    def _add_origin_feat(self) -> None:
        """Grant origin feat from background."""
        feat_name = BACKGROUNDS[self.background].get("origin_feat")
        if feat_name:
            feat = Feat.objects.get(name=feat_name)
            CharacterFeat.objects.create(
                character=self.character, feat=feat, granted_by="background"
            )

    def _add_starting_gold(self) -> None:
        """Add 50 GP starting equipment (2024 rules)."""
        self.character.inventory.gp += 50
        self.character.inventory.save()

    def _select_personality_trait(self) -> None:
        self.character.personality_trait = random.choice(
            list(BACKGROUNDS[self.background]["personality_traits"].values())
        )

    def _select_ideal(self) -> None:
        self.character.ideal = random.choice(
            list(BACKGROUNDS[self.background]["ideals"].values())
        )

    def _select_bond(self) -> None:
        self.character.bond = random.choice(
            list(BACKGROUNDS[self.background]["bonds"].values())
        )

    def _select_flaw(self) -> None:
        self.character.flaw = random.choice(
            list(BACKGROUNDS[self.background]["flaws"].values())
        )

    def build(self) -> None:
        self._add_skill_proficiencies()
        self._add_tool_proficiency()
        self._add_origin_feat()
        self._add_starting_gold()
        self._select_personality_trait()
        self._select_ideal()
        self._select_bond()
        self._select_flaw()
        self.character.save()


class DerivedStatsBuilder(CharacterAttributesBuilder):
    """Calculate and apply derived statistics for a character.

    Handles stats that depend on other character attributes being set:
    - Passive Perception: 10 + WIS modifier + proficiency bonus (if proficient)
    - Initiative is DEX modifier (computed property, no storage needed)
    - AC is calculated when armor is equipped (handled by Inventory)
    """

    def __init__(self, character: Character) -> None:
        self.character = character

    def _calculate_passive_perception(self) -> int:
        """Calculate passive Perception score.

        Formula: 10 + Wisdom modifier + proficiency bonus (if proficient in Perception)
        """
        base = 10
        wis_mod = self.character.wisdom.modifier

        # Check if character has Perception proficiency
        has_perception_proficiency = SkillProficiency.objects.filter(
            character=self.character, skill__name=SkillName.PERCEPTION
        ).exists()

        proficiency_bonus = (
            self.character.proficiency_bonus if has_perception_proficiency else 0
        )

        return base + wis_mod + proficiency_bonus

    def build(self) -> None:
        # Passive perception is a derived stat that we store for convenience
        # It's used frequently for stealth checks and hidden enemies
        # Note: We don't have a field for this yet, so this is calculated on demand
        # If needed, add a passive_perception field to Character model
        pass


class SpellcastingBuilder(CharacterAttributesBuilder):
    """Set up spellcasting for classes that have spell slots.

    Only runs for classes with a ClassSpellcasting configuration.
    Creates CharacterSpellSlot records based on the SpellSlotTable.
    """

    def __init__(self, character: Character, klass: Class) -> None:
        self.character = character
        self.klass = klass
        self._spellcasting: ClassSpellcasting | None = None

    def _get_spellcasting_config(self) -> ClassSpellcasting | None:
        """Get the ClassSpellcasting config for this class, if it exists."""
        if self._spellcasting is None:
            try:
                self._spellcasting = self.klass.spellcasting
            except ClassSpellcasting.DoesNotExist:
                pass
        return self._spellcasting

    def _is_spellcaster(self) -> bool:
        """Check if this class has spellcasting abilities."""
        config = self._get_spellcasting_config()
        return config is not None and config.is_caster

    def _setup_spell_slots(self) -> None:
        """Create CharacterSpellSlot records based on class level."""
        char_class = self.character.character_classes.get(klass=self.klass)
        class_level = char_class.level

        # Get spell slots for this class and level from the reference table
        slot_data = SpellSlotTable.objects.filter(
            class_name=self.klass.name, class_level=class_level
        )

        for slot in slot_data:
            if slot.slots > 0:
                CharacterSpellSlot.objects.create(
                    character=self.character,
                    slot_level=slot.slot_level,
                    total=slot.slots,
                    used=0,
                )

    def _setup_warlock_pact_magic(self) -> None:
        """Set up Warlock's Pact Magic spell slots."""
        char_class = self.character.character_classes.get(klass=self.klass)
        class_level = char_class.level

        # Warlock Pact Magic progression
        # Level 1: 1 slot at level 1
        # Level 2: 2 slots at level 1
        # Level 3-4: 2 slots at level 2
        # Level 5-6: 2 slots at level 3
        # etc.
        if class_level >= 1:
            slots = 1 if class_level == 1 else 2
            slot_level = min((class_level + 1) // 2, 5)  # Max level 5 slots
            WarlockSpellSlot.objects.create(
                character=self.character,
                slot_level=slot_level,
                total=slots,
                used=0,
            )

    def build(self) -> None:
        """Set up spellcasting if the class supports it."""
        if not self._is_spellcaster():
            return

        config = self._get_spellcasting_config()
        if config is None:
            return

        # Handle Warlock's unique Pact Magic system
        if config.caster_type == "pact":
            self._setup_warlock_pact_magic()
        else:
            # Standard spellcasting (full, half, third casters)
            self._setup_spell_slots()
