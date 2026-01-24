"""Comprehensive tests for character attribute builders.

Tests cover:
- SpeciesBuilder: darkvision, size, speed, languages
- ClassBuilder: proficiencies (armor, weapon), class features
- DerivedStatsBuilder: passive perception calculation
- SpellcastingBuilder: spell slot setup for casters
"""

import pytest

from character.character_attributes_builders import (
    ClassBuilder,
    DerivedStatsBuilder,
    SpeciesBuilder,
    SpellcastingBuilder,
)
from character.constants.classes import ClassName
from character.constants.equipment import ArmorType, WeaponType
from character.constants.skills import SkillName
from character.constants.spells import CasterType, SpellcastingAbility
from character.models.classes import CharacterFeature
from character.models.proficiencies import (
    ArmorProficiency,
    SkillProficiency,
    WeaponProficiency,
)
from character.models.skills import Skill
from character.models.spells import CharacterSpellSlot, WarlockSpellSlot

from .factories import (
    AbilityTypeFactory,
    ArmorSettingsFactory,
    CharacterClassFactory,
    CharacterFactory,
    ClassFactory,
    ClassFeatureFactory,
    ClassSpellcastingFactory,
    SpeciesFactory,
    SpellSlotTableFactory,
    WeponSettingsFactory,
)


# =============================================================================
# SpeciesBuilder Tests
# =============================================================================


@pytest.mark.django_db
class TestSpeciesBuilder:
    def test_apply_darkvision(self):
        """Test that darkvision is applied from species."""
        species = SpeciesFactory(name="test_dwarf_dv", darkvision=60)
        character = CharacterFactory(species=species)
        SpeciesBuilder(character).build()

        assert character.darkvision == 60

    def test_no_darkvision(self):
        """Test that species without darkvision sets 0."""
        species = SpeciesFactory(name="test_human_nodv", darkvision=0)
        character = CharacterFactory(species=species)
        SpeciesBuilder(character).build()

        assert character.darkvision == 0

    def test_apply_size(self):
        """Test that size is applied from species."""
        species = SpeciesFactory(name="test_size_m", size="M")
        character = CharacterFactory(species=species)
        SpeciesBuilder(character).build()

        assert character.size == "M"

    def test_apply_speed(self):
        """Test that speed is applied from species."""
        species = SpeciesFactory(name="test_speed_25", speed=25)
        character = CharacterFactory(species=species)
        SpeciesBuilder(character).build()

        assert character.speed == 25

    def test_no_species(self):
        """Test SpeciesBuilder handles character without species."""
        character = CharacterFactory(species=None)
        SpeciesBuilder(character).build()
        assert character.darkvision == 0

    def test_superior_darkvision(self):
        """Test species with 120ft darkvision."""
        species = SpeciesFactory(name="test_drow_dv120", darkvision=120)
        character = CharacterFactory(species=species)
        SpeciesBuilder(character).build()

        assert character.darkvision == 120

    def test_small_size_species(self):
        """Test small size species."""
        species = SpeciesFactory(name="test_halfling_s", size="S", speed=25)
        character = CharacterFactory(species=species)
        SpeciesBuilder(character).build()

        assert character.size == "S"
        assert character.speed == 25


# =============================================================================
# ClassBuilder Tests - Armor Proficiencies
# =============================================================================


@pytest.fixture
def armor_settings():
    """Create armor settings for each type."""
    return [
        ArmorSettingsFactory(name="Test Leather", armor_type=ArmorType.LIGHT_ARMOR),
        ArmorSettingsFactory(name="Test Chain", armor_type=ArmorType.HEAVY_ARMOR),
        ArmorSettingsFactory(name="Test Scale", armor_type=ArmorType.MEDIUM_ARMOR),
        ArmorSettingsFactory(name="Test Shield", armor_type=ArmorType.SHIELD),
    ]


@pytest.fixture
def weapon_settings():
    """Create weapon settings for simple and martial weapons."""
    return [
        WeponSettingsFactory(name="Test Club", weapon_type=WeaponType.SIMPLE_MELEE),
        WeponSettingsFactory(name="Test Dagger", weapon_type=WeaponType.SIMPLE_MELEE),
        WeponSettingsFactory(
            name="Test Shortbow", weapon_type=WeaponType.SIMPLE_RANGED
        ),
        WeponSettingsFactory(
            name="Test Longsword", weapon_type=WeaponType.MARTIAL_MELEE
        ),
        WeponSettingsFactory(
            name="Test Longbow", weapon_type=WeaponType.MARTIAL_RANGED
        ),
    ]


@pytest.mark.django_db
class TestClassBuilderArmorProficiencies:
    def test_apply_armor_proficiencies_all(self, armor_settings):
        """Test class gets all armor proficiencies."""
        str_type = AbilityTypeFactory(name="STR")
        klass = ClassFactory(
            name="test_fighter_all_armor",
            primary_ability=str_type,
            armor_proficiencies=["LA", "MA", "HA", "SH"],
        )
        character = CharacterFactory()
        ClassBuilder(character, klass)._apply_armor_proficiencies()

        profs = ArmorProficiency.objects.filter(character=character)
        assert profs.count() == 4

    def test_apply_armor_proficiencies_none(self, armor_settings):
        """Test class with no armor proficiencies."""
        int_type = AbilityTypeFactory(name="INT")
        klass = ClassFactory(
            name="test_wizard_no_armor",
            primary_ability=int_type,
            armor_proficiencies=[],
        )
        character = CharacterFactory()
        ClassBuilder(character, klass)._apply_armor_proficiencies()

        profs = ArmorProficiency.objects.filter(character=character)
        assert profs.count() == 0

    def test_light_armor_only(self, armor_settings):
        """Test class with only light armor proficiency."""
        dex_type = AbilityTypeFactory(name="DEX")
        klass = ClassFactory(
            name="test_rogue_la_only",
            primary_ability=dex_type,
            armor_proficiencies=["LA"],
        )
        character = CharacterFactory()
        ClassBuilder(character, klass)._apply_armor_proficiencies()

        profs = ArmorProficiency.objects.filter(character=character)
        assert profs.count() == 1
        assert profs.first().armor.name == "Test Leather"

    def test_light_medium_shield(self, armor_settings):
        """Test class with light, medium armor and shields."""
        wis_type = AbilityTypeFactory(name="WIS")
        klass = ClassFactory(
            name="test_cleric_lms",
            primary_ability=wis_type,
            armor_proficiencies=["LA", "MA", "SH"],
        )
        character = CharacterFactory()
        ClassBuilder(character, klass)._apply_armor_proficiencies()

        profs = ArmorProficiency.objects.filter(character=character)
        assert profs.count() == 3


# =============================================================================
# ClassBuilder Tests - Weapon Proficiencies
# =============================================================================


@pytest.mark.django_db
class TestClassBuilderWeaponProficiencies:
    def test_apply_weapon_proficiencies_all(self, weapon_settings):
        """Test class gets all weapon proficiencies."""
        str_type = AbilityTypeFactory(name="STR")
        klass = ClassFactory(
            name="test_fighter_all_wpn",
            primary_ability=str_type,
            weapon_proficiencies=["simple", "martial"],
        )
        character = CharacterFactory()
        ClassBuilder(character, klass)._apply_weapon_proficiencies()

        profs = WeaponProficiency.objects.filter(character=character)
        assert profs.count() == 5

    def test_apply_weapon_proficiencies_simple(self, weapon_settings):
        """Test class gets only simple weapon proficiencies."""
        int_type = AbilityTypeFactory(name="INT")
        klass = ClassFactory(
            name="test_wizard_simple_wpn",
            primary_ability=int_type,
            weapon_proficiencies=["simple"],
        )
        character = CharacterFactory()
        ClassBuilder(character, klass)._apply_weapon_proficiencies()

        profs = WeaponProficiency.objects.filter(character=character)
        assert profs.count() == 3  # Club, Dagger, Shortbow

    def test_no_weapon_proficiencies(self, weapon_settings):
        """Test class with no weapon proficiencies."""
        cha_type = AbilityTypeFactory(name="CHA")
        klass = ClassFactory(
            name="test_sorc_no_wpn",
            primary_ability=cha_type,
            weapon_proficiencies=[],
        )
        character = CharacterFactory()
        ClassBuilder(character, klass)._apply_weapon_proficiencies()

        profs = WeaponProficiency.objects.filter(character=character)
        assert profs.count() == 0

    def test_martial_only(self, weapon_settings):
        """Test class with only martial proficiencies."""
        str_type = AbilityTypeFactory(name="STR")
        klass = ClassFactory(
            name="test_barb_martial",
            primary_ability=str_type,
            weapon_proficiencies=["martial"],
        )
        character = CharacterFactory()
        ClassBuilder(character, klass)._apply_weapon_proficiencies()

        profs = WeaponProficiency.objects.filter(character=character)
        assert profs.count() == 2  # Longsword, Longbow


# =============================================================================
# ClassBuilder Tests - Class Features
# =============================================================================


@pytest.mark.django_db
class TestClassBuilderFeatures:
    def test_apply_class_features_level_1(self):
        """Test that level 1 class features are applied."""
        str_type = AbilityTypeFactory(name="STR")
        klass = ClassFactory(name="test_fighter_feat1", primary_ability=str_type)
        ClassFeatureFactory(klass=klass, name="Fighting Style", level=1)
        ClassFeatureFactory(klass=klass, name="Second Wind", level=1)
        ClassFeatureFactory(klass=klass, name="Action Surge", level=2)  # Not applied

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=1)
        ClassBuilder(character, klass)._apply_class_features()

        char_features = CharacterFeature.objects.filter(character=character)
        assert char_features.count() == 2
        feature_names = {cf.class_feature.name for cf in char_features}
        assert "Fighting Style" in feature_names
        assert "Second Wind" in feature_names
        assert "Action Surge" not in feature_names

    def test_class_feature_source_tracking(self):
        """Test that feature source class is correctly tracked."""
        str_type = AbilityTypeFactory(name="STR")
        klass = ClassFactory(name="test_fighter_src", primary_ability=str_type)
        feature = ClassFeatureFactory(klass=klass, name="Test Feature", level=1)

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=1)
        ClassBuilder(character, klass)._apply_class_features()

        char_feature = CharacterFeature.objects.get(
            character=character, class_feature=feature
        )
        assert char_feature.source_class == klass
        assert char_feature.level_gained == 1

    def test_no_level_1_features(self):
        """Test class with no level 1 features."""
        str_type = AbilityTypeFactory(name="STR")
        klass = ClassFactory(name="test_fighter_nol1", primary_ability=str_type)
        ClassFeatureFactory(klass=klass, name="Action Surge", level=2)

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=1)
        ClassBuilder(character, klass)._apply_class_features()

        char_features = CharacterFeature.objects.filter(character=character)
        assert char_features.count() == 0

    def test_many_level_1_features(self):
        """Test class with many level 1 features."""
        dex_type = AbilityTypeFactory(name="DEX")
        klass = ClassFactory(name="test_monk_many", primary_ability=dex_type)
        ClassFeatureFactory(klass=klass, name="Unarmored Defense", level=1)
        ClassFeatureFactory(klass=klass, name="Martial Arts", level=1)
        ClassFeatureFactory(klass=klass, name="Deft Strike", level=1)

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=1)
        ClassBuilder(character, klass)._apply_class_features()

        char_features = CharacterFeature.objects.filter(character=character)
        assert char_features.count() == 3


# =============================================================================
# DerivedStatsBuilder Tests
# =============================================================================


@pytest.fixture
def perception_skill(db):
    """Create Perception skill."""
    wis_type = AbilityTypeFactory(name="WIS")
    skill, _ = Skill.objects.get_or_create(
        name=SkillName.PERCEPTION,
        defaults={
            "ability_type": wis_type,
            "description": "Perception check description.",
        },
    )
    return skill


@pytest.mark.django_db
class TestDerivedStatsBuilder:
    def test_passive_perception_without_proficiency(self, perception_skill):
        """Test passive perception calculation without proficiency."""
        character = CharacterFactory()
        builder = DerivedStatsBuilder(character)

        wis_mod = character.wisdom.modifier
        expected = 10 + wis_mod

        assert builder._calculate_passive_perception() == expected

    def test_passive_perception_with_proficiency(self, perception_skill):
        """Test passive perception calculation with proficiency."""
        character = CharacterFactory()
        SkillProficiency.objects.create(character=character, skill=perception_skill)
        builder = DerivedStatsBuilder(character)

        wis_mod = character.wisdom.modifier
        prof_bonus = character.proficiency_bonus
        expected = 10 + wis_mod + prof_bonus

        assert builder._calculate_passive_perception() == expected

    def test_passive_perception_higher_level(self, perception_skill):
        """Test passive perception at higher levels."""
        character = CharacterFactory()
        character.level = 5  # Proficiency bonus = +3
        character.save()
        SkillProficiency.objects.create(character=character, skill=perception_skill)
        builder = DerivedStatsBuilder(character)

        wis_mod = character.wisdom.modifier
        expected = 10 + wis_mod + 3

        assert builder._calculate_passive_perception() == expected


# =============================================================================
# SpellcastingBuilder Tests
# =============================================================================


@pytest.mark.django_db
class TestSpellcastingBuilder:
    def test_is_spellcaster_true(self):
        """Test spellcaster is identified correctly."""
        int_type = AbilityTypeFactory(name="INT")
        klass = ClassFactory(name="test_wiz_caster", primary_ability=int_type)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PREPARED,
            spellcasting_ability=SpellcastingAbility.INTELLIGENCE,
        )

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass)
        builder = SpellcastingBuilder(character, klass)

        assert builder._is_spellcaster() is True

    def test_is_not_spellcaster(self):
        """Test non-caster is identified correctly."""
        str_type = AbilityTypeFactory(name="STR")
        klass = ClassFactory(name="test_ftr_nocaster", primary_ability=str_type)
        # No ClassSpellcasting created

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass)
        builder = SpellcastingBuilder(character, klass)

        assert builder._is_spellcaster() is False

    def test_setup_spell_slots(self):
        """Test spell slot setup from SpellSlotTable."""
        int_type = AbilityTypeFactory(name="INT")
        # Use real ClassName for SpellSlotTable compatibility
        klass = ClassFactory(name=ClassName.WIZARD, primary_ability=int_type)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PREPARED,
            spellcasting_ability=SpellcastingAbility.INTELLIGENCE,
        )
        # Create spell slot entry for wizard level 1
        SpellSlotTableFactory(
            class_name=ClassName.WIZARD, class_level=1, slot_level=1, slots=2
        )

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=1)
        SpellcastingBuilder(character, klass).build()

        slots = CharacterSpellSlot.objects.filter(character=character)
        assert slots.count() == 1
        assert slots.first().slot_level == 1
        assert slots.first().total == 2

    def test_setup_warlock_pact_magic_level_1(self):
        """Test Warlock Pact Magic setup at level 1."""
        cha_type = AbilityTypeFactory(name="CHA")
        klass = ClassFactory(name="test_wlk_pact1", primary_ability=cha_type)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PACT,
            spellcasting_ability=SpellcastingAbility.CHARISMA,
        )

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=1)
        SpellcastingBuilder(character, klass).build()

        pact_slot = WarlockSpellSlot.objects.get(character=character)
        assert pact_slot.slot_level == 1
        assert pact_slot.total == 1

    def test_setup_warlock_pact_magic_level_2(self):
        """Test Warlock Pact Magic setup at level 2."""
        cha_type = AbilityTypeFactory(name="CHA")
        klass = ClassFactory(name="test_wlk_pact2", primary_ability=cha_type)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PACT,
            spellcasting_ability=SpellcastingAbility.CHARISMA,
        )

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=2)
        SpellcastingBuilder(character, klass).build()

        pact_slot = WarlockSpellSlot.objects.get(character=character)
        assert pact_slot.slot_level == 1
        assert pact_slot.total == 2

    def test_setup_warlock_pact_magic_level_5(self):
        """Test Warlock Pact Magic setup at level 5."""
        cha_type = AbilityTypeFactory(name="CHA")
        klass = ClassFactory(name="test_wlk_pact5", primary_ability=cha_type)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PACT,
            spellcasting_ability=SpellcastingAbility.CHARISMA,
        )

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=5)
        SpellcastingBuilder(character, klass).build()

        pact_slot = WarlockSpellSlot.objects.get(character=character)
        assert pact_slot.slot_level == 3
        assert pact_slot.total == 2

    def test_non_caster_no_spell_slots(self):
        """Test non-caster doesn't get spell slots."""
        str_type = AbilityTypeFactory(name="STR")
        klass = ClassFactory(name="test_ftr_noslots", primary_ability=str_type)

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass)
        SpellcastingBuilder(character, klass).build()

        slots = CharacterSpellSlot.objects.filter(character=character)
        assert slots.count() == 0
        pact_slots = WarlockSpellSlot.objects.filter(character=character)
        assert pact_slots.count() == 0

    def test_wizard_multiple_slot_levels(self):
        """Test caster with multiple spell slot levels."""
        int_type = AbilityTypeFactory(name="INT")
        # Use a unique class_level (99) to avoid conflicts
        klass = ClassFactory(name=ClassName.WIZARD, primary_ability=int_type)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PREPARED,
            spellcasting_ability=SpellcastingAbility.INTELLIGENCE,
        )
        SpellSlotTableFactory(
            class_name=ClassName.WIZARD, class_level=99, slot_level=1, slots=4
        )
        SpellSlotTableFactory(
            class_name=ClassName.WIZARD, class_level=99, slot_level=2, slots=2
        )

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=99)
        SpellcastingBuilder(character, klass).build()

        slots = CharacterSpellSlot.objects.filter(character=character).order_by(
            "slot_level"
        )
        assert slots.count() == 2
        assert slots[0].slot_level == 1
        assert slots[0].total == 4
        assert slots[1].slot_level == 2
        assert slots[1].total == 2


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.django_db
class TestBuilderIntegration:
    def test_full_martial_character_build(self, armor_settings, weapon_settings):
        """Test building a full martial character."""
        str_type = AbilityTypeFactory(name="STR")
        con_type = AbilityTypeFactory(name="CON")

        klass = ClassFactory(
            name="test_ftr_integ",
            hit_die=10,
            hp_first_level=10,
            hp_higher_levels=6,
            primary_ability=str_type,
            armor_proficiencies=["LA", "MA", "HA", "SH"],
            weapon_proficiencies=["simple", "martial"],
            starting_wealth_dice="5d4",
        )
        klass.saving_throws.add(str_type, con_type)
        ClassFeatureFactory(klass=klass, name="Fighting Style", level=1)

        species = SpeciesFactory(
            name="test_human_integ", size="M", speed=30, darkvision=0
        )
        character = CharacterFactory(species=species)

        SpeciesBuilder(character).build()
        ClassBuilder(character, klass).build()
        DerivedStatsBuilder(character).build()
        SpellcastingBuilder(character, klass).build()

        assert character.darkvision == 0
        assert character.size == "M"
        assert character.speed == 30
        assert ArmorProficiency.objects.filter(character=character).count() == 4
        assert WeaponProficiency.objects.filter(character=character).count() == 5
        assert CharacterFeature.objects.filter(character=character).count() == 1
        assert CharacterSpellSlot.objects.filter(character=character).count() == 0

    def test_full_spellcaster_build(self, armor_settings, weapon_settings):
        """Test building a full spellcaster character."""
        int_type = AbilityTypeFactory(name="INT")
        wis_type = AbilityTypeFactory(name="WIS")

        # Use real ClassName and unique class_level for SpellSlotTable
        klass = ClassFactory(
            name=ClassName.WIZARD,
            hit_die=6,
            hp_first_level=6,
            hp_higher_levels=4,
            primary_ability=int_type,
            armor_proficiencies=[],
            weapon_proficiencies=["simple"],
            starting_wealth_dice="4d4",
        )
        klass.saving_throws.add(int_type, wis_type)

        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PREPARED,
            spellcasting_ability=SpellcastingAbility.INTELLIGENCE,
        )
        SpellSlotTableFactory(
            class_name=ClassName.WIZARD, class_level=98, slot_level=1, slots=2
        )
        ClassFeatureFactory(klass=klass, name="Arcane Recovery", level=1)

        species = SpeciesFactory(
            name="test_elf_integ", size="M", speed=30, darkvision=60
        )
        character = CharacterFactory(species=species)

        SpeciesBuilder(character).build()
        CharacterClassFactory(character=character, klass=klass, level=98)
        # Don't call ClassBuilder.build() as it creates CharacterClass again
        ClassBuilder(character, klass)._apply_hit_points()
        ClassBuilder(character, klass)._apply_armor_proficiencies()
        ClassBuilder(character, klass)._apply_weapon_proficiencies()
        ClassBuilder(character, klass)._apply_class_features()
        DerivedStatsBuilder(character).build()
        SpellcastingBuilder(character, klass).build()

        assert character.darkvision == 60
        assert ArmorProficiency.objects.filter(character=character).count() == 0
        assert WeaponProficiency.objects.filter(character=character).count() == 3
        assert CharacterFeature.objects.filter(character=character).count() == 1
        assert CharacterSpellSlot.objects.filter(character=character).count() == 1

    def test_warlock_full_build(self, armor_settings, weapon_settings):
        """Test building a Warlock with Pact Magic."""
        cha_type = AbilityTypeFactory(name="CHA")
        wis_type = AbilityTypeFactory(name="WIS")

        klass = ClassFactory(
            name="test_wlk_integ",
            hit_die=8,
            hp_first_level=8,
            hp_higher_levels=5,
            primary_ability=cha_type,
            armor_proficiencies=["LA"],
            weapon_proficiencies=["simple"],
            starting_wealth_dice="4d4",
        )
        klass.saving_throws.add(cha_type, wis_type)

        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PACT,
            spellcasting_ability=SpellcastingAbility.CHARISMA,
        )
        ClassFeatureFactory(klass=klass, name="Pact Magic", level=1)

        species = SpeciesFactory(
            name="test_tiefling_integ", size="M", speed=30, darkvision=60
        )
        character = CharacterFactory(species=species)

        SpeciesBuilder(character).build()
        ClassBuilder(character, klass).build()
        DerivedStatsBuilder(character).build()
        SpellcastingBuilder(character, klass).build()

        assert character.darkvision == 60
        assert ArmorProficiency.objects.filter(character=character).count() == 1
        assert WeaponProficiency.objects.filter(character=character).count() == 3
        assert CharacterFeature.objects.filter(character=character).count() == 1
        assert CharacterSpellSlot.objects.filter(character=character).count() == 0
        pact_slot = WarlockSpellSlot.objects.get(character=character)
        assert pact_slot.total == 1
