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


@pytest.fixture
def species_with_darkvision():
    """Create a species with darkvision."""
    return SpeciesFactory(
        name="dwarf",
        size="M",
        speed=25,
        darkvision=60,
    )


@pytest.fixture
def species_without_darkvision():
    """Create a species without darkvision."""
    return SpeciesFactory(
        name="human",
        size="M",
        speed=30,
        darkvision=0,
    )


@pytest.mark.django_db
class TestSpeciesBuilder:
    def test_apply_darkvision(self, species_with_darkvision):
        """Test that darkvision is applied from species."""
        character = CharacterFactory(species=species_with_darkvision)
        builder = SpeciesBuilder(character)
        builder.build()

        assert character.darkvision == 60

    def test_no_darkvision(self, species_without_darkvision):
        """Test that species without darkvision sets 0."""
        character = CharacterFactory(species=species_without_darkvision)
        builder = SpeciesBuilder(character)
        builder.build()

        assert character.darkvision == 0

    def test_apply_size(self, species_with_darkvision):
        """Test that size is applied from species."""
        character = CharacterFactory(species=species_with_darkvision)
        builder = SpeciesBuilder(character)
        builder.build()

        assert character.size == "M"

    def test_apply_speed(self, species_with_darkvision):
        """Test that speed is applied from species."""
        character = CharacterFactory(species=species_with_darkvision)
        builder = SpeciesBuilder(character)
        builder.build()

        assert character.speed == 25


# =============================================================================
# ClassBuilder Tests - Armor Proficiencies
# =============================================================================


@pytest.fixture
def fighter_class_with_armor():
    """Create a Fighter class with full armor proficiencies."""
    str_type = AbilityTypeFactory(name="STR")
    klass = ClassFactory(
        name=ClassName.FIGHTER,
        hit_die=10,
        hp_first_level=10,
        hp_higher_levels=6,
        primary_ability=str_type,
        armor_proficiencies=["LA", "MA", "HA", "SH"],
        weapon_proficiencies=["simple", "martial"],
        starting_wealth_dice="5d4",
    )
    return klass


@pytest.fixture
def wizard_class_no_armor():
    """Create a Wizard class with no armor proficiencies."""
    int_type = AbilityTypeFactory(name="INT")
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
    return klass


@pytest.fixture
def armor_settings():
    """Create armor settings for each type."""
    return [
        ArmorSettingsFactory(name="Leather", armor_type=ArmorType.LIGHT_ARMOR),
        ArmorSettingsFactory(name="Chain mail", armor_type=ArmorType.HEAVY_ARMOR),
        ArmorSettingsFactory(name="Scale mail", armor_type=ArmorType.MEDIUM_ARMOR),
        ArmorSettingsFactory(name="Shield", armor_type=ArmorType.SHIELD),
    ]


@pytest.mark.django_db
class TestClassBuilderArmorProficiencies:
    def test_apply_armor_proficiencies_fighter(
        self, fighter_class_with_armor, armor_settings
    ):
        """Test Fighter gets all armor proficiencies."""
        character = CharacterFactory()
        builder = ClassBuilder(character, fighter_class_with_armor)
        builder._apply_armor_proficiencies()

        profs = ArmorProficiency.objects.filter(character=character)
        # Should have proficiency in all 4 armor pieces
        assert profs.count() == 4

    def test_apply_armor_proficiencies_wizard(
        self, wizard_class_no_armor, armor_settings
    ):
        """Test Wizard gets no armor proficiencies."""
        character = CharacterFactory()
        builder = ClassBuilder(character, wizard_class_no_armor)
        builder._apply_armor_proficiencies()

        profs = ArmorProficiency.objects.filter(character=character)
        assert profs.count() == 0

    def test_armor_proficiency_types(self, fighter_class_with_armor, armor_settings):
        """Test that correct armor types are granted."""
        character = CharacterFactory()
        builder = ClassBuilder(character, fighter_class_with_armor)
        builder._apply_armor_proficiencies()

        armor_names = {
            p.armor.name for p in ArmorProficiency.objects.filter(character=character)
        }
        assert "Leather" in armor_names
        assert "Chain mail" in armor_names
        assert "Scale mail" in armor_names
        assert "Shield" in armor_names


# =============================================================================
# ClassBuilder Tests - Weapon Proficiencies
# =============================================================================


@pytest.fixture
def weapon_settings():
    """Create weapon settings for simple and martial weapons."""
    return [
        WeponSettingsFactory(name="Club", weapon_type=WeaponType.SIMPLE_MELEE),
        WeponSettingsFactory(name="Dagger", weapon_type=WeaponType.SIMPLE_MELEE),
        WeponSettingsFactory(name="Shortbow", weapon_type=WeaponType.SIMPLE_RANGED),
        WeponSettingsFactory(name="Longsword", weapon_type=WeaponType.MARTIAL_MELEE),
        WeponSettingsFactory(name="Longbow", weapon_type=WeaponType.MARTIAL_RANGED),
    ]


@pytest.mark.django_db
class TestClassBuilderWeaponProficiencies:
    def test_apply_weapon_proficiencies_fighter(
        self, fighter_class_with_armor, weapon_settings
    ):
        """Test Fighter gets all weapon proficiencies."""
        character = CharacterFactory()
        builder = ClassBuilder(character, fighter_class_with_armor)
        builder._apply_weapon_proficiencies()

        profs = WeaponProficiency.objects.filter(character=character)
        # Should have proficiency in all 5 weapons (simple + martial)
        assert profs.count() == 5

    def test_apply_weapon_proficiencies_wizard(
        self, wizard_class_no_armor, weapon_settings
    ):
        """Test Wizard gets only simple weapon proficiencies."""
        character = CharacterFactory()
        builder = ClassBuilder(character, wizard_class_no_armor)
        builder._apply_weapon_proficiencies()

        profs = WeaponProficiency.objects.filter(character=character)
        # Should have proficiency in only 3 simple weapons
        assert profs.count() == 3

        weapon_names = {p.weapon.name for p in profs}
        assert "Club" in weapon_names
        assert "Dagger" in weapon_names
        assert "Shortbow" in weapon_names
        assert "Longsword" not in weapon_names
        assert "Longbow" not in weapon_names

    def test_no_weapon_proficiencies(self, weapon_settings):
        """Test class with no weapon proficiencies."""
        int_type = AbilityTypeFactory(name="INT")
        klass = ClassFactory(
            name=ClassName.SORCERER,
            primary_ability=int_type,
            armor_proficiencies=[],
            weapon_proficiencies=[],
        )
        character = CharacterFactory()
        builder = ClassBuilder(character, klass)
        builder._apply_weapon_proficiencies()

        profs = WeaponProficiency.objects.filter(character=character)
        assert profs.count() == 0


# =============================================================================
# ClassBuilder Tests - Class Features
# =============================================================================


@pytest.mark.django_db
class TestClassBuilderFeatures:
    def test_apply_class_features_level_1(self):
        """Test that level 1 class features are applied."""
        str_type = AbilityTypeFactory(name="STR")
        klass = ClassFactory(name=ClassName.FIGHTER, primary_ability=str_type)
        ClassFeatureFactory(klass=klass, name="Fighting Style", level=1)
        ClassFeatureFactory(klass=klass, name="Second Wind", level=1)
        # Level 2 feature should not be applied
        ClassFeatureFactory(klass=klass, name="Action Surge", level=2)

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=1)
        builder = ClassBuilder(character, klass)
        builder._apply_class_features()

        char_features = CharacterFeature.objects.filter(character=character)
        assert char_features.count() == 2

        feature_names = {cf.class_feature.name for cf in char_features}
        assert "Fighting Style" in feature_names
        assert "Second Wind" in feature_names
        assert "Action Surge" not in feature_names

    def test_class_feature_source_tracking(self):
        """Test that feature source class is correctly tracked."""
        str_type = AbilityTypeFactory(name="STR")
        klass = ClassFactory(name=ClassName.FIGHTER, primary_ability=str_type)
        feature = ClassFeatureFactory(klass=klass, name="Test Feature", level=1)

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=1)
        builder = ClassBuilder(character, klass)
        builder._apply_class_features()

        char_feature = CharacterFeature.objects.get(
            character=character, class_feature=feature
        )
        assert char_feature.source_class == klass
        assert char_feature.level_gained == 1


# =============================================================================
# DerivedStatsBuilder Tests
# =============================================================================


@pytest.fixture
def perception_skill(db):
    """Create Perception skill."""
    wis_type = AbilityTypeFactory(name="WIS")
    return Skill.objects.create(
        name=SkillName.PERCEPTION,
        ability_type=wis_type,
        description="Your Wisdom (Perception) check lets you spot, hear, or otherwise detect the presence of something.",
    )


@pytest.mark.django_db
class TestDerivedStatsBuilder:
    def test_passive_perception_without_proficiency(self, perception_skill):
        """Test passive perception calculation without proficiency."""
        character = CharacterFactory()
        builder = DerivedStatsBuilder(character)

        # Passive Perception = 10 + WIS modifier
        wis_mod = character.wisdom.modifier
        expected = 10 + wis_mod

        assert builder._calculate_passive_perception() == expected

    def test_passive_perception_with_proficiency(self, perception_skill):
        """Test passive perception calculation with proficiency."""
        character = CharacterFactory()
        SkillProficiency.objects.create(character=character, skill=perception_skill)
        builder = DerivedStatsBuilder(character)

        # Passive Perception = 10 + WIS modifier + proficiency bonus
        wis_mod = character.wisdom.modifier
        prof_bonus = character.proficiency_bonus
        expected = 10 + wis_mod + prof_bonus

        assert builder._calculate_passive_perception() == expected


# =============================================================================
# SpellcastingBuilder Tests
# =============================================================================


@pytest.fixture
def wizard_spellcaster():
    """Create a Wizard with spellcasting configuration."""
    int_type = AbilityTypeFactory(name="INT")
    klass = ClassFactory(
        name=ClassName.WIZARD,
        primary_ability=int_type,
    )
    ClassSpellcastingFactory(
        klass=klass,
        caster_type=CasterType.PREPARED,
        spellcasting_ability=SpellcastingAbility.INTELLIGENCE,
        learns_cantrips=True,
        spell_list_access=True,
        ritual_casting=True,
    )
    return klass


@pytest.fixture
def warlock_spellcaster():
    """Create a Warlock with Pact Magic."""
    cha_type = AbilityTypeFactory(name="CHA")
    klass = ClassFactory(
        name=ClassName.WARLOCK,
        primary_ability=cha_type,
    )
    ClassSpellcastingFactory(
        klass=klass,
        caster_type=CasterType.PACT,
        spellcasting_ability=SpellcastingAbility.CHARISMA,
        learns_cantrips=True,
    )
    return klass


@pytest.fixture
def non_caster():
    """Create a Fighter with no spellcasting."""
    str_type = AbilityTypeFactory(name="STR")
    return ClassFactory(
        name=ClassName.FIGHTER,
        primary_ability=str_type,
    )


@pytest.mark.django_db
class TestSpellcastingBuilder:
    def test_is_spellcaster_wizard(self, wizard_spellcaster):
        """Test wizard is identified as spellcaster."""
        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=wizard_spellcaster)
        builder = SpellcastingBuilder(character, wizard_spellcaster)

        assert builder._is_spellcaster() is True

    def test_is_not_spellcaster_fighter(self, non_caster):
        """Test fighter is not identified as spellcaster."""
        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=non_caster)
        builder = SpellcastingBuilder(character, non_caster)

        assert builder._is_spellcaster() is False

    def test_setup_spell_slots_wizard(self, wizard_spellcaster):
        """Test spell slot setup for Wizard."""
        # Create spell slot table entries
        SpellSlotTableFactory(
            class_name=ClassName.WIZARD, class_level=1, slot_level=1, slots=2
        )

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=wizard_spellcaster, level=1)
        builder = SpellcastingBuilder(character, wizard_spellcaster)
        builder.build()

        slots = CharacterSpellSlot.objects.filter(character=character)
        assert slots.count() == 1
        slot = slots.first()
        assert slot.slot_level == 1
        assert slot.total == 2
        assert slot.used == 0

    def test_setup_warlock_pact_magic(self, warlock_spellcaster):
        """Test Warlock Pact Magic setup."""
        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=warlock_spellcaster, level=1)
        builder = SpellcastingBuilder(character, warlock_spellcaster)
        builder.build()

        pact_slot = WarlockSpellSlot.objects.get(character=character)
        assert pact_slot.slot_level == 1
        assert pact_slot.total == 1
        assert pact_slot.used == 0

    def test_non_caster_no_spell_slots(self, non_caster):
        """Test non-caster doesn't get spell slots."""
        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=non_caster)
        builder = SpellcastingBuilder(character, non_caster)
        builder.build()

        slots = CharacterSpellSlot.objects.filter(character=character)
        assert slots.count() == 0

        pact_slots = WarlockSpellSlot.objects.filter(character=character)
        assert pact_slots.count() == 0


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.django_db
class TestBuilderIntegration:
    def test_full_martial_character_build(self, armor_settings, weapon_settings):
        """Test building a full martial character (Fighter)."""
        str_type = AbilityTypeFactory(name="STR")
        con_type = AbilityTypeFactory(name="CON")

        klass = ClassFactory(
            name=ClassName.FIGHTER,
            hit_die=10,
            hp_first_level=10,
            hp_higher_levels=6,
            primary_ability=str_type,
            armor_proficiencies=["LA", "MA", "HA", "SH"],
            weapon_proficiencies=["simple", "martial"],
            starting_wealth_dice="5d4",
        )
        klass.saving_throws.add(str_type, con_type)

        # Add a level 1 feature
        ClassFeatureFactory(klass=klass, name="Fighting Style", level=1)

        species = SpeciesFactory(name="human", size="M", speed=30, darkvision=0)
        character = CharacterFactory(species=species)

        # Build in sequence
        SpeciesBuilder(character).build()
        ClassBuilder(character, klass).build()
        DerivedStatsBuilder(character).build()
        SpellcastingBuilder(character, klass).build()

        # Verify all aspects
        assert character.darkvision == 0
        assert character.size == "M"
        assert character.speed == 30

        assert ArmorProficiency.objects.filter(character=character).count() == 4
        assert WeaponProficiency.objects.filter(character=character).count() == 5
        assert CharacterFeature.objects.filter(character=character).count() == 1
        assert CharacterSpellSlot.objects.filter(character=character).count() == 0

    def test_full_spellcaster_character_build(self, armor_settings, weapon_settings):
        """Test building a full spellcaster character (Wizard)."""
        int_type = AbilityTypeFactory(name="INT")
        wis_type = AbilityTypeFactory(name="WIS")

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

        # Add spellcasting config
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PREPARED,
            spellcasting_ability=SpellcastingAbility.INTELLIGENCE,
        )

        # Add spell slot table entry
        SpellSlotTableFactory(
            class_name=ClassName.WIZARD, class_level=1, slot_level=1, slots=2
        )

        # Add a level 1 feature
        ClassFeatureFactory(klass=klass, name="Arcane Recovery", level=1)

        species = SpeciesFactory(name="elf", size="M", speed=30, darkvision=60)
        character = CharacterFactory(species=species)

        # Build in sequence
        SpeciesBuilder(character).build()
        ClassBuilder(character, klass).build()
        DerivedStatsBuilder(character).build()
        SpellcastingBuilder(character, klass).build()

        # Verify all aspects
        assert character.darkvision == 60
        assert ArmorProficiency.objects.filter(character=character).count() == 0
        # Only simple weapons (3 of them in fixture)
        assert WeaponProficiency.objects.filter(character=character).count() == 3
        assert CharacterFeature.objects.filter(character=character).count() == 1
        # Should have spell slots
        assert CharacterSpellSlot.objects.filter(character=character).count() == 1


# =============================================================================
# Extended SpeciesBuilder Tests
# =============================================================================


@pytest.mark.django_db
class TestSpeciesBuilderExtended:
    def test_no_species(self):
        """Test SpeciesBuilder handles character without species."""
        character = CharacterFactory(species=None)
        builder = SpeciesBuilder(character)
        # Should not raise
        builder.build()
        # Darkvision should remain at default
        assert character.darkvision == 0

    def test_superior_darkvision(self):
        """Test species with 120ft darkvision (e.g., Drow)."""
        species = SpeciesFactory(
            name="tiefling",
            size="M",
            speed=30,
            darkvision=120,
        )
        character = CharacterFactory(species=species)
        builder = SpeciesBuilder(character)
        builder.build()

        assert character.darkvision == 120

    def test_small_size_species(self):
        """Test small size species (e.g., Halfling, Gnome)."""
        species = SpeciesFactory(
            name="halfling",
            size="S",
            speed=25,
            darkvision=0,
        )
        character = CharacterFactory(species=species)
        builder = SpeciesBuilder(character)
        builder.build()

        assert character.size == "S"
        assert character.speed == 25


# =============================================================================
# Extended ClassBuilder Armor Proficiency Tests
# =============================================================================


@pytest.mark.django_db
class TestClassBuilderArmorProficienciesExtended:
    def test_light_armor_only(self, armor_settings):
        """Test class with only light armor proficiency (e.g., Bard, Rogue)."""
        dex_type = AbilityTypeFactory(name="DEX")
        klass = ClassFactory(
            name=ClassName.ROGUE,
            primary_ability=dex_type,
            armor_proficiencies=["LA"],
            weapon_proficiencies=["simple"],
        )
        character = CharacterFactory()
        builder = ClassBuilder(character, klass)
        builder._apply_armor_proficiencies()

        profs = ArmorProficiency.objects.filter(character=character)
        # Only light armor
        assert profs.count() == 1
        assert profs.first().armor.name == "Leather"

    def test_light_medium_shield(self, armor_settings):
        """Test class with light, medium armor and shields (e.g., Cleric)."""
        wis_type = AbilityTypeFactory(name="WIS")
        klass = ClassFactory(
            name=ClassName.CLERIC,
            primary_ability=wis_type,
            armor_proficiencies=["LA", "MA", "SH"],
            weapon_proficiencies=["simple"],
        )
        character = CharacterFactory()
        builder = ClassBuilder(character, klass)
        builder._apply_armor_proficiencies()

        profs = ArmorProficiency.objects.filter(character=character)
        # Light, medium, and shield (3 pieces)
        assert profs.count() == 3

        armor_names = {p.armor.name for p in profs}
        assert "Leather" in armor_names
        assert "Scale mail" in armor_names
        assert "Shield" in armor_names
        assert "Chain mail" not in armor_names  # Heavy armor excluded


# =============================================================================
# Extended ClassBuilder Weapon Proficiency Tests
# =============================================================================


@pytest.mark.django_db
class TestClassBuilderWeaponProficienciesExtended:
    def test_martial_only(self, weapon_settings):
        """Test class with only martial proficiencies (theoretical)."""
        str_type = AbilityTypeFactory(name="STR")
        klass = ClassFactory(
            name=ClassName.BARBARIAN,
            primary_ability=str_type,
            armor_proficiencies=[],
            weapon_proficiencies=["martial"],
        )
        character = CharacterFactory()
        builder = ClassBuilder(character, klass)
        builder._apply_weapon_proficiencies()

        profs = WeaponProficiency.objects.filter(character=character)
        # Only martial weapons (2 in fixture: Longsword, Longbow)
        assert profs.count() == 2

        weapon_names = {p.weapon.name for p in profs}
        assert "Longsword" in weapon_names
        assert "Longbow" in weapon_names
        assert "Club" not in weapon_names
        assert "Dagger" not in weapon_names


# =============================================================================
# Extended ClassBuilder Class Features Tests
# =============================================================================


@pytest.mark.django_db
class TestClassBuilderFeaturesExtended:
    def test_no_level_1_features(self):
        """Test class with no level 1 features."""
        str_type = AbilityTypeFactory(name="STR")
        klass = ClassFactory(name=ClassName.FIGHTER, primary_ability=str_type)
        # Only add higher level features
        ClassFeatureFactory(klass=klass, name="Action Surge", level=2)
        ClassFeatureFactory(klass=klass, name="Extra Attack", level=5)

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=1)
        builder = ClassBuilder(character, klass)
        builder._apply_class_features()

        char_features = CharacterFeature.objects.filter(character=character)
        assert char_features.count() == 0

    def test_many_level_1_features(self):
        """Test class with many level 1 features."""
        str_type = AbilityTypeFactory(name="STR")
        klass = ClassFactory(name=ClassName.MONK, primary_ability=str_type)
        # Monks get several features at level 1
        ClassFeatureFactory(klass=klass, name="Unarmored Defense", level=1)
        ClassFeatureFactory(klass=klass, name="Martial Arts", level=1)
        ClassFeatureFactory(klass=klass, name="Deft Strike", level=1)
        ClassFeatureFactory(klass=klass, name="Patient Defense", level=1)
        ClassFeatureFactory(klass=klass, name="Step of the Wind", level=1)

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=1)
        builder = ClassBuilder(character, klass)
        builder._apply_class_features()

        char_features = CharacterFeature.objects.filter(character=character)
        assert char_features.count() == 5


# =============================================================================
# Extended DerivedStatsBuilder Tests
# =============================================================================


@pytest.mark.django_db
class TestDerivedStatsBuilderExtended:
    def test_passive_perception_higher_level(self, perception_skill):
        """Test passive perception at higher levels (proficiency bonus increases)."""
        character = CharacterFactory()
        character.level = 5  # Proficiency bonus = +3
        character.save()
        SkillProficiency.objects.create(character=character, skill=perception_skill)
        builder = DerivedStatsBuilder(character)

        wis_mod = character.wisdom.modifier
        # At level 5, proficiency bonus is +3
        expected = 10 + wis_mod + 3

        assert builder._calculate_passive_perception() == expected

    def test_passive_perception_level_9(self, perception_skill):
        """Test passive perception at level 9 (proficiency bonus +4)."""
        character = CharacterFactory()
        character.level = 9
        character.save()
        SkillProficiency.objects.create(character=character, skill=perception_skill)
        builder = DerivedStatsBuilder(character)

        wis_mod = character.wisdom.modifier
        # At level 9, proficiency bonus is +4
        expected = 10 + wis_mod + 4

        assert builder._calculate_passive_perception() == expected

    def test_passive_perception_level_17(self, perception_skill):
        """Test passive perception at level 17 (proficiency bonus +6)."""
        character = CharacterFactory()
        character.level = 17
        character.save()
        SkillProficiency.objects.create(character=character, skill=perception_skill)
        builder = DerivedStatsBuilder(character)

        wis_mod = character.wisdom.modifier
        # At level 17, proficiency bonus is +6
        expected = 10 + wis_mod + 6

        assert builder._calculate_passive_perception() == expected


# =============================================================================
# Extended SpellcastingBuilder Tests
# =============================================================================


@pytest.mark.django_db
class TestSpellcastingBuilderExtended:
    def test_warlock_level_2(self):
        """Test Warlock at level 2 (2 slots at level 1)."""
        cha_type = AbilityTypeFactory(name="CHA")
        klass = ClassFactory(name=ClassName.WARLOCK, primary_ability=cha_type)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PACT,
            spellcasting_ability=SpellcastingAbility.CHARISMA,
        )

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=2)
        builder = SpellcastingBuilder(character, klass)
        builder.build()

        pact_slot = WarlockSpellSlot.objects.get(character=character)
        assert pact_slot.slot_level == 1
        assert pact_slot.total == 2  # Level 2 warlocks have 2 slots

    def test_warlock_level_3(self):
        """Test Warlock at level 3 (2 slots at level 2)."""
        cha_type = AbilityTypeFactory(name="CHA")
        klass = ClassFactory(name=ClassName.WARLOCK, primary_ability=cha_type)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PACT,
            spellcasting_ability=SpellcastingAbility.CHARISMA,
        )

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=3)
        builder = SpellcastingBuilder(character, klass)
        builder.build()

        pact_slot = WarlockSpellSlot.objects.get(character=character)
        assert pact_slot.slot_level == 2  # Level 3-4 use 2nd level slots
        assert pact_slot.total == 2

    def test_warlock_level_5(self):
        """Test Warlock at level 5 (2 slots at level 3)."""
        cha_type = AbilityTypeFactory(name="CHA")
        klass = ClassFactory(name=ClassName.WARLOCK, primary_ability=cha_type)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PACT,
            spellcasting_ability=SpellcastingAbility.CHARISMA,
        )

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=5)
        builder = SpellcastingBuilder(character, klass)
        builder.build()

        pact_slot = WarlockSpellSlot.objects.get(character=character)
        assert pact_slot.slot_level == 3  # Level 5-6 use 3rd level slots
        assert pact_slot.total == 2

    def test_wizard_multiple_slot_levels(self):
        """Test Wizard with multiple spell slot levels (level 3)."""
        int_type = AbilityTypeFactory(name="INT")
        klass = ClassFactory(name=ClassName.WIZARD, primary_ability=int_type)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PREPARED,
            spellcasting_ability=SpellcastingAbility.INTELLIGENCE,
        )

        # Level 3 wizard has 4 1st-level and 2 2nd-level slots
        SpellSlotTableFactory(
            class_name=ClassName.WIZARD, class_level=3, slot_level=1, slots=4
        )
        SpellSlotTableFactory(
            class_name=ClassName.WIZARD, class_level=3, slot_level=2, slots=2
        )

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=3)
        builder = SpellcastingBuilder(character, klass)
        builder.build()

        slots = CharacterSpellSlot.objects.filter(character=character).order_by(
            "slot_level"
        )
        assert slots.count() == 2

        slot_1 = slots[0]
        assert slot_1.slot_level == 1
        assert slot_1.total == 4

        slot_2 = slots[1]
        assert slot_2.slot_level == 2
        assert slot_2.total == 2

    def test_half_caster_paladin(self):
        """Test half-caster (Paladin) spell slot setup."""
        str_type = AbilityTypeFactory(name="STR")
        klass = ClassFactory(name=ClassName.PALADIN, primary_ability=str_type)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PREPARED,
            spellcasting_ability=SpellcastingAbility.CHARISMA,
        )

        # Level 2 paladin gets 2 1st-level slots
        SpellSlotTableFactory(
            class_name=ClassName.PALADIN, class_level=2, slot_level=1, slots=2
        )

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass, level=2)
        builder = SpellcastingBuilder(character, klass)
        builder.build()

        slots = CharacterSpellSlot.objects.filter(character=character)
        assert slots.count() == 1
        assert slots.first().slot_level == 1
        assert slots.first().total == 2

    def test_spellcasting_config_caching(self):
        """Test that spellcasting config is cached after first access."""
        int_type = AbilityTypeFactory(name="INT")
        klass = ClassFactory(name=ClassName.WIZARD, primary_ability=int_type)
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PREPARED,
            spellcasting_ability=SpellcastingAbility.INTELLIGENCE,
        )

        character = CharacterFactory()
        CharacterClassFactory(character=character, klass=klass)
        builder = SpellcastingBuilder(character, klass)

        # First call should load config
        config1 = builder._get_spellcasting_config()
        # Second call should return cached config
        config2 = builder._get_spellcasting_config()

        assert config1 is config2


# =============================================================================
# Additional Integration Tests
# =============================================================================


@pytest.mark.django_db
class TestBuilderIntegrationExtended:
    def test_half_caster_build(self, armor_settings, weapon_settings):
        """Test building a half-caster character (Paladin)."""
        str_type = AbilityTypeFactory(name="STR")
        cha_type = AbilityTypeFactory(name="CHA")

        klass = ClassFactory(
            name=ClassName.PALADIN,
            hit_die=10,
            hp_first_level=10,
            hp_higher_levels=6,
            primary_ability=str_type,
            armor_proficiencies=["LA", "MA", "HA", "SH"],
            weapon_proficiencies=["simple", "martial"],
            starting_wealth_dice="5d4",
        )
        klass.saving_throws.add(str_type, cha_type)

        # Add spellcasting config
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PREPARED,
            spellcasting_ability=SpellcastingAbility.CHARISMA,
        )

        # Level 2 paladin spell slots
        SpellSlotTableFactory(
            class_name=ClassName.PALADIN, class_level=2, slot_level=1, slots=2
        )

        # Add level 1 features
        ClassFeatureFactory(klass=klass, name="Divine Sense", level=1)
        ClassFeatureFactory(klass=klass, name="Lay on Hands", level=1)

        species = SpeciesFactory(name="human", size="M", speed=30, darkvision=0)
        character = CharacterFactory(species=species)

        # Build in sequence (level 2 for spellcasting)
        SpeciesBuilder(character).build()
        CharacterClassFactory(character=character, klass=klass, level=2)
        ClassBuilder(character, klass).build()
        DerivedStatsBuilder(character).build()
        SpellcastingBuilder(character, klass).build()

        # Verify martial aspects
        assert ArmorProficiency.objects.filter(character=character).count() == 4
        assert WeaponProficiency.objects.filter(character=character).count() == 5
        assert CharacterFeature.objects.filter(character=character).count() == 2

        # Verify spellcasting aspects
        slots = CharacterSpellSlot.objects.filter(character=character)
        assert slots.count() == 1
        assert slots.first().total == 2

    def test_warlock_full_build(self, armor_settings, weapon_settings):
        """Test building a Warlock with Pact Magic."""
        cha_type = AbilityTypeFactory(name="CHA")
        wis_type = AbilityTypeFactory(name="WIS")

        klass = ClassFactory(
            name=ClassName.WARLOCK,
            hit_die=8,
            hp_first_level=8,
            hp_higher_levels=5,
            primary_ability=cha_type,
            armor_proficiencies=["LA"],
            weapon_proficiencies=["simple"],
            starting_wealth_dice="4d4",
        )
        klass.saving_throws.add(cha_type, wis_type)

        # Add Pact Magic config
        ClassSpellcastingFactory(
            klass=klass,
            caster_type=CasterType.PACT,
            spellcasting_ability=SpellcastingAbility.CHARISMA,
        )

        # Add level 1 features
        ClassFeatureFactory(klass=klass, name="Pact Magic", level=1)
        ClassFeatureFactory(klass=klass, name="Eldritch Invocations", level=1)

        species = SpeciesFactory(name="tiefling", size="M", speed=30, darkvision=60)
        character = CharacterFactory(species=species)

        # Build in sequence
        SpeciesBuilder(character).build()
        ClassBuilder(character, klass).build()
        DerivedStatsBuilder(character).build()
        SpellcastingBuilder(character, klass).build()

        # Verify all aspects
        assert character.darkvision == 60

        # Light armor only
        assert ArmorProficiency.objects.filter(character=character).count() == 1

        # Simple weapons only (3 in fixture)
        assert WeaponProficiency.objects.filter(character=character).count() == 3

        # Class features
        assert CharacterFeature.objects.filter(character=character).count() == 2

        # Warlock uses Pact Magic, not regular spell slots
        assert CharacterSpellSlot.objects.filter(character=character).count() == 0
        pact_slot = WarlockSpellSlot.objects.get(character=character)
        assert pact_slot.slot_level == 1
        assert pact_slot.total == 1

    def test_build_order_matters(self, armor_settings, weapon_settings):
        """Test that building in correct order produces valid character."""
        str_type = AbilityTypeFactory(name="STR")
        klass = ClassFactory(
            name=ClassName.FIGHTER,
            primary_ability=str_type,
            armor_proficiencies=["LA", "MA", "HA", "SH"],
            weapon_proficiencies=["simple", "martial"],
        )

        species = SpeciesFactory(name="dwarf", size="M", speed=25, darkvision=60)
        character = CharacterFactory(species=species)

        # Build in correct order
        SpeciesBuilder(character).build()
        ClassBuilder(character, klass).build()
        DerivedStatsBuilder(character).build()
        SpellcastingBuilder(character, klass).build()

        # Character should have all expected attributes
        assert character.darkvision == 60
        assert character.speed == 25
        assert character.size == "M"
        assert ArmorProficiency.objects.filter(character=character).exists()
        assert WeaponProficiency.objects.filter(character=character).exists()
