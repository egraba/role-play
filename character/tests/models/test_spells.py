import pytest

from character.constants.classes import ClassName
from character.constants.spells import (
    CasterType,
    CastingTime,
    SpellDuration,
    SpellLevel,
    SpellRange,
    SpellSchool,
    SpellcastingAbility,
)
from character.models.spells import (
    CharacterSpellSlot,
    ClassSpellcasting,
    Concentration,
    Spell,
    SpellPreparation,
    SpellSettings,
    SpellSlotTable,
    WarlockSpellSlot,
)

from ..factories import (
    CharacterFactory,
    CharacterSpellSlotFactory,
    ClassFactory,
    ClassSpellcastingFactory,
    ConcentrationFactory,
    SpellFactory,
    SpellPreparationFactory,
    SpellSettingsFactory,
    SpellSlotTableFactory,
    WarlockSpellSlotFactory,
)


@pytest.mark.django_db
class TestSpellSettingsModel:
    def test_creation(self):
        spell = SpellSettingsFactory(
            name="Fireball",
            level=SpellLevel.THIRD,
            school=SpellSchool.EVOCATION,
            casting_time=CastingTime.ACTION,
            range=SpellRange.FEET_150,
            components=["V", "S", "M"],
            material_components="A tiny ball of bat guano and sulfur",
            duration=SpellDuration.INSTANTANEOUS,
            concentration=False,
            ritual=False,
            description="A bright streak flashes from your pointing finger...",
            classes=["wizard", "sorcerer"],
        )
        assert spell.name == "Fireball"
        assert spell.level == SpellLevel.THIRD
        assert spell.school == SpellSchool.EVOCATION
        assert spell.casting_time == CastingTime.ACTION
        assert spell.range == SpellRange.FEET_150
        assert "V" in spell.components
        assert spell.concentration is False
        assert spell.ritual is False

    def test_str(self):
        spell = SpellSettingsFactory(name="Magic Missile", level=SpellLevel.FIRST)
        assert str(spell) == "Magic Missile (Level 1)"

    def test_str_cantrip(self):
        spell = SpellSettingsFactory(name="Fire Bolt", level=SpellLevel.CANTRIP)
        assert str(spell) == "Fire Bolt (Cantrip)"

    def test_is_cantrip_property(self):
        cantrip = SpellSettingsFactory(level=SpellLevel.CANTRIP)
        leveled = SpellSettingsFactory(level=SpellLevel.FIRST)
        assert cantrip.is_cantrip is True
        assert leveled.is_cantrip is False

    def test_all_schools_valid(self):
        for school, _ in SpellSchool.choices:
            spell = SpellSettingsFactory(school=school)
            assert spell.school == school

    def test_all_levels_valid(self):
        for level, _ in SpellLevel.choices:
            spell = SpellSettingsFactory(level=level)
            assert spell.level == level

    def test_ordering(self):
        SpellSettingsFactory(name="AAA Spell", level=SpellLevel.THIRD)
        SpellSettingsFactory(name="ZZZ Spell", level=SpellLevel.FIRST)
        SpellSettingsFactory(name="MMM Spell", level=SpellLevel.CANTRIP)

        spells = list(SpellSettings.objects.all())
        # Should be ordered by level first, then name
        assert spells[0].level <= spells[-1].level


@pytest.mark.django_db
class TestSpellModel:
    def test_creation(self):
        character = CharacterFactory()
        spell_settings = SpellSettingsFactory()
        spell = Spell.objects.create(
            character=character, settings=spell_settings, source="class"
        )
        assert spell.character == character
        assert spell.settings == spell_settings
        assert spell.source == "class"

    def test_str(self):
        spell = SpellFactory()
        assert spell.character.name in str(spell)
        assert spell.settings.name in str(spell)

    def test_unique_together_constraint(self):
        character = CharacterFactory()
        spell_settings = SpellSettingsFactory()
        Spell.objects.create(character=character, settings=spell_settings)
        with pytest.raises(Exception):
            Spell.objects.create(character=character, settings=spell_settings)

    def test_character_spells_known_relation(self):
        character = CharacterFactory()
        spell1 = SpellFactory(character=character)
        spell2 = SpellFactory(character=character)

        assert character.spells_known.count() == 2
        assert spell1 in character.spells_known.all()
        assert spell2 in character.spells_known.all()

    def test_cascade_delete_on_character(self):
        spell = SpellFactory()
        character_id = spell.character.id
        spell.character.delete()
        assert not Spell.objects.filter(character_id=character_id).exists()


@pytest.mark.django_db
class TestSpellPreparationModel:
    def test_creation(self):
        character = CharacterFactory()
        spell_settings = SpellSettingsFactory()
        prep = SpellPreparation.objects.create(
            character=character, settings=spell_settings, always_prepared=False
        )
        assert prep.character == character
        assert prep.settings == spell_settings
        assert prep.always_prepared is False

    def test_str(self):
        prep = SpellPreparationFactory()
        assert "prepared" in str(prep)

    def test_always_prepared_flag(self):
        prep = SpellPreparationFactory(always_prepared=True)
        assert prep.always_prepared is True

    def test_unique_together_constraint(self):
        character = CharacterFactory()
        spell_settings = SpellSettingsFactory()
        SpellPreparation.objects.create(character=character, settings=spell_settings)
        with pytest.raises(Exception):
            SpellPreparation.objects.create(
                character=character, settings=spell_settings
            )

    def test_character_prepared_spells_relation(self):
        character = CharacterFactory()
        prep1 = SpellPreparationFactory(character=character)
        SpellPreparationFactory(character=character)

        assert character.prepared_spells.count() == 2
        assert prep1 in character.prepared_spells.all()


@pytest.mark.django_db
class TestSpellSlotTableModel:
    def test_creation(self):
        slot_table = SpellSlotTable.objects.create(
            class_name=ClassName.WIZARD, class_level=1, slot_level=1, slots=2
        )
        assert slot_table.class_name == ClassName.WIZARD
        assert slot_table.class_level == 1
        assert slot_table.slot_level == 1
        assert slot_table.slots == 2

    def test_str(self):
        slot_table = SpellSlotTableFactory(
            class_name=ClassName.WIZARD, class_level=5, slot_level=3, slots=2
        )
        assert "wizard" in str(slot_table)
        assert "L5" in str(slot_table)
        assert "L3" in str(slot_table)

    def test_unique_together_constraint(self):
        SpellSlotTable.objects.create(
            class_name=ClassName.WIZARD, class_level=1, slot_level=1, slots=2
        )
        with pytest.raises(Exception):
            SpellSlotTable.objects.create(
                class_name=ClassName.WIZARD, class_level=1, slot_level=1, slots=3
            )


@pytest.mark.django_db
class TestCharacterSpellSlotModel:
    def test_creation(self):
        character = CharacterFactory()
        slot = CharacterSpellSlot.objects.create(
            character=character, slot_level=1, total=2, used=0
        )
        assert slot.character == character
        assert slot.slot_level == 1
        assert slot.total == 2
        assert slot.used == 0

    def test_remaining_property(self):
        slot = CharacterSpellSlotFactory(total=4, used=1)
        assert slot.remaining == 3

    def test_str(self):
        slot = CharacterSpellSlotFactory(slot_level=2, total=3, used=1)
        assert "L2" in str(slot)
        assert "2/3" in str(slot)

    def test_use_slot_success(self):
        slot = CharacterSpellSlotFactory(total=2, used=0)
        result = slot.use_slot()
        assert result is True
        assert slot.used == 1
        assert slot.remaining == 1

    def test_use_slot_failure_no_slots(self):
        slot = CharacterSpellSlotFactory(total=2, used=2)
        result = slot.use_slot()
        assert result is False
        assert slot.used == 2

    def test_restore_slot(self):
        slot = CharacterSpellSlotFactory(total=4, used=3)
        slot.restore_slot(2)
        assert slot.used == 1
        assert slot.remaining == 3

    def test_restore_slot_not_below_zero(self):
        slot = CharacterSpellSlotFactory(total=4, used=1)
        slot.restore_slot(5)
        assert slot.used == 0

    def test_restore_all(self):
        slot = CharacterSpellSlotFactory(total=4, used=4)
        slot.restore_all()
        assert slot.used == 0
        assert slot.remaining == 4

    def test_unique_together_constraint(self):
        character = CharacterFactory()
        CharacterSpellSlot.objects.create(
            character=character, slot_level=1, total=2, used=0
        )
        with pytest.raises(Exception):
            CharacterSpellSlot.objects.create(
                character=character, slot_level=1, total=3, used=0
            )

    def test_character_spell_slots_relation(self):
        character = CharacterFactory()
        slot1 = CharacterSpellSlotFactory(character=character, slot_level=1)
        CharacterSpellSlotFactory(character=character, slot_level=2)

        assert character.spell_slots.count() == 2
        assert slot1 in character.spell_slots.all()


@pytest.mark.django_db
class TestWarlockSpellSlotModel:
    def test_creation(self):
        character = CharacterFactory()
        pact_magic = WarlockSpellSlot.objects.create(
            character=character, slot_level=1, total=1, used=0
        )
        assert pact_magic.character == character
        assert pact_magic.slot_level == 1
        assert pact_magic.total == 1

    def test_remaining_property(self):
        pact_magic = WarlockSpellSlotFactory(total=2, used=1)
        assert pact_magic.remaining == 1

    def test_str(self):
        pact_magic = WarlockSpellSlotFactory(slot_level=3, total=2, used=1)
        assert "Pact Magic" in str(pact_magic)
        assert "L3" in str(pact_magic)

    def test_use_slot_success(self):
        pact_magic = WarlockSpellSlotFactory(total=2, used=0)
        result = pact_magic.use_slot()
        assert result is True
        assert pact_magic.used == 1

    def test_use_slot_failure_no_slots(self):
        pact_magic = WarlockSpellSlotFactory(total=2, used=2)
        result = pact_magic.use_slot()
        assert result is False

    def test_restore_all(self):
        pact_magic = WarlockSpellSlotFactory(total=2, used=2)
        pact_magic.restore_all()
        assert pact_magic.used == 0
        assert pact_magic.remaining == 2

    def test_one_to_one_constraint(self):
        character = CharacterFactory()
        WarlockSpellSlot.objects.create(character=character, slot_level=1, total=1)
        with pytest.raises(Exception):
            WarlockSpellSlot.objects.create(character=character, slot_level=2, total=2)

    def test_character_pact_magic_relation(self):
        character = CharacterFactory()
        pact_magic = WarlockSpellSlotFactory(character=character)
        assert character.pact_magic == pact_magic


@pytest.mark.django_db
class TestClassSpellcastingModel:
    def test_creation(self):
        klass = ClassFactory(name=ClassName.WIZARD)
        spellcasting = ClassSpellcasting.objects.create(
            klass=klass,
            caster_type=CasterType.PREPARED,
            spellcasting_ability=SpellcastingAbility.INTELLIGENCE,
            learns_cantrips=True,
            spell_list_access=True,
            ritual_casting=True,
            spellcasting_focus="arcane focus",
        )
        assert spellcasting.klass == klass
        assert spellcasting.caster_type == CasterType.PREPARED
        assert spellcasting.spellcasting_ability == SpellcastingAbility.INTELLIGENCE

    def test_str_caster(self):
        spellcasting = ClassSpellcastingFactory(
            caster_type=CasterType.PREPARED,
            spellcasting_ability=SpellcastingAbility.WISDOM,
        )
        assert "prepared" in str(spellcasting).lower()
        assert "wisdom" in str(spellcasting).lower()

    def test_str_non_caster(self):
        klass = ClassFactory(name=ClassName.FIGHTER)
        spellcasting = ClassSpellcasting.objects.create(
            klass=klass, caster_type="", spellcasting_ability=""
        )
        assert "Non-caster" in str(spellcasting)

    def test_is_caster_property(self):
        klass1 = ClassFactory()
        klass2 = ClassFactory()
        caster = ClassSpellcastingFactory(klass=klass1, caster_type=CasterType.KNOWN)
        non_caster = ClassSpellcastingFactory(klass=klass2, caster_type="")
        assert caster.is_caster is True
        assert non_caster.is_caster is False

    def test_one_to_one_constraint(self):
        klass = ClassFactory()
        ClassSpellcasting.objects.create(klass=klass, caster_type=CasterType.PREPARED)
        with pytest.raises(Exception):
            ClassSpellcasting.objects.create(klass=klass, caster_type=CasterType.KNOWN)

    def test_class_spellcasting_relation(self):
        klass = ClassFactory()
        spellcasting = ClassSpellcastingFactory(klass=klass)
        assert klass.spellcasting == spellcasting


@pytest.mark.django_db
class TestConcentrationModel:
    def test_creation(self):
        character = CharacterFactory()
        spell = SpellSettingsFactory(concentration=True)
        concentration = Concentration.objects.create(character=character, spell=spell)
        assert concentration.character == character
        assert concentration.spell == spell

    def test_str(self):
        concentration = ConcentrationFactory()
        assert "concentrating on" in str(concentration)

    def test_break_concentration(self):
        concentration = ConcentrationFactory()
        character_id = concentration.character.id
        concentration.break_concentration()
        assert not Concentration.objects.filter(character_id=character_id).exists()

    def test_start_concentration(self):
        character = CharacterFactory()
        spell = SpellSettingsFactory(concentration=True)
        concentration = Concentration.start_concentration(character, spell, rounds=10)
        assert concentration.character == character
        assert concentration.spell == spell
        assert concentration.rounds_remaining == 10

    def test_start_concentration_breaks_existing(self):
        character = CharacterFactory()
        spell1 = SpellSettingsFactory(name="Spell One", concentration=True)
        spell2 = SpellSettingsFactory(name="Spell Two", concentration=True)

        conc1 = Concentration.start_concentration(character, spell1)
        assert character.concentration == conc1

        conc2 = Concentration.start_concentration(character, spell2)
        assert character.concentration == conc2
        assert not Concentration.objects.filter(spell=spell1).exists()

    def test_one_to_one_constraint(self):
        character = CharacterFactory()
        spell1 = SpellSettingsFactory(concentration=True)
        spell2 = SpellSettingsFactory(concentration=True)
        Concentration.objects.create(character=character, spell=spell1)
        with pytest.raises(Exception):
            Concentration.objects.create(character=character, spell=spell2)

    def test_character_concentration_relation(self):
        character = CharacterFactory()
        concentration = ConcentrationFactory(character=character)
        assert character.concentration == concentration

    def test_cascade_delete_on_character(self):
        concentration = ConcentrationFactory()
        character_id = concentration.character.id
        concentration.character.delete()
        assert not Concentration.objects.filter(character_id=character_id).exists()
