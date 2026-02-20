import factory

from character.constants.classes import ClassName
from magic.constants.spells import (
    CasterType,
    CastingTime,
    EffectDurationType,
    SpellDamageType,
    SpellDuration,
    SpellEffectType,
    SpellLevel,
    SpellRange,
    SpellSaveEffect,
    SpellSaveType,
    SpellSchool,
    SpellTargetType,
    SpellcastingAbility,
)
from magic.models.spell_effects import (
    ActiveSpellEffect,
    SpellEffectTemplate,
    SummonedCreature,
)
from magic.models.spells import (
    CharacterSpellSlot,
    ClassSpellcasting,
    Concentration,
    Spell,
    SpellPreparation,
    SpellSettings,
    SpellSlotTable,
    WarlockSpellSlot,
)


class SpellSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpellSettings
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Test Spell {n}")
    level = SpellLevel.FIRST
    school = factory.Faker("random_element", elements=SpellSchool)
    casting_time = CastingTime.ACTION
    range = SpellRange.FEET_60
    components = ["V", "S"]
    duration = SpellDuration.INSTANTANEOUS
    concentration = False
    ritual = False
    description = factory.Faker("text", max_nb_chars=500)
    classes = ["wizard", "sorcerer"]


class SpellFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Spell

    # Lazy string avoids circular import with character.tests.factories
    character = factory.SubFactory("character.tests.factories.CharacterFactory")
    settings = factory.SubFactory(SpellSettingsFactory)
    source = "class"


class SpellPreparationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpellPreparation

    character = factory.SubFactory("character.tests.factories.CharacterFactory")
    settings = factory.SubFactory(SpellSettingsFactory)
    always_prepared = False


class SpellSlotTableFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpellSlotTable
        django_get_or_create = ("class_name", "class_level", "slot_level")

    class_name = ClassName.WIZARD
    class_level = 1
    slot_level = 1
    slots = 2


class CharacterSpellSlotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CharacterSpellSlot

    character = factory.SubFactory("character.tests.factories.CharacterFactory")
    slot_level = 1
    total = 2
    used = 0


class WarlockSpellSlotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WarlockSpellSlot

    character = factory.SubFactory("character.tests.factories.CharacterFactory")
    slot_level = 1
    total = 1
    used = 0


class ClassSpellcastingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClassSpellcasting
        django_get_or_create = ("klass",)

    # Lazy string avoids circular import with character.tests.factories
    klass = factory.SubFactory("character.tests.factories.ClassFactory")
    caster_type = CasterType.PREPARED
    spellcasting_ability = SpellcastingAbility.INTELLIGENCE
    learns_cantrips = True
    spell_list_access = True
    ritual_casting = True
    spellcasting_focus = "arcane focus"


class ConcentrationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Concentration

    character = factory.SubFactory("character.tests.factories.CharacterFactory")
    spell = factory.SubFactory(SpellSettingsFactory, concentration=True)


class SpellEffectTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpellEffectTemplate

    spell = factory.SubFactory(SpellSettingsFactory)
    effect_type = SpellEffectType.DAMAGE
    target_type = SpellTargetType.SINGLE
    damage_type = SpellDamageType.FIRE
    base_dice = "8d6"
    dice_per_level = "1d6"
    save_type = SpellSaveType.DEXTERITY
    save_effect = SpellSaveEffect.HALF_DAMAGE
    duration_type = EffectDurationType.INSTANTANEOUS


class ActiveSpellEffectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActiveSpellEffect

    character = factory.SubFactory("character.tests.factories.CharacterFactory")
    template = factory.SubFactory(SpellEffectTemplateFactory)
    caster = factory.SubFactory("character.tests.factories.CharacterFactory")
    rounds_remaining = 10
    is_concentration = False


class SummonedCreatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SummonedCreature

    summoner = factory.SubFactory("character.tests.factories.CharacterFactory")
    spell = factory.SubFactory(SpellSettingsFactory)
    name = factory.Faker("first_name")
    hp_current = 20
    hp_max = 20
    ac = 13
    rounds_remaining = 10
    is_concentration = True
