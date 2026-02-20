import factory

# Re-exports for backward compatibility
from bestiary.tests.factories import (  # noqa: F401
    LairActionTemplateFactory,
    LegendaryActionTemplateFactory,
    MonsterActionTemplateFactory,
    MonsterConditionImmunityFactory,
    MonsterDamageRelationFactory,
    MonsterFactory,
    MonsterLanguageFactory,
    MonsterMultiattackFactory,
    MonsterReactionFactory,
    MonsterSavingThrowFactory,
    MonsterSenseFactory,
    MonsterSettingsFactory,
    MonsterSkillFactory,
    MonsterSpeedFactory,
    MonsterTraitFactory,
    MultiattackActionFactory,
)
from equipment.tests.factories import (  # noqa: F401
    ArmorFactory,
    ArmorSettingsFactory,
    AttunementFactory,
    GearFactory,
    GearSettingsFactory,
    InventoryFactory,
    MagicItemFactory,
    MagicItemSettingsFactory,
    PackFactory,
    PackSettingsFactory,
    ToolFactory,
    ToolSettingsFactory,
    WeaponFactory,
    WeponSettingsFactory,
)
from magic.tests.factories import (  # noqa: F401
    ActiveSpellEffectFactory,
    CharacterSpellSlotFactory,
    ClassSpellcastingFactory,
    ConcentrationFactory,
    SpellEffectTemplateFactory,
    SpellFactory,
    SpellPreparationFactory,
    SpellSettingsFactory,
    SpellSlotTableFactory,
    SummonedCreatureFactory,
    WarlockSpellSlotFactory,
)

# Character-specific imports
from character.constants.abilities import AbilityName
from character.constants.backgrounds import Background
from character.constants.classes import ClassName
from character.constants.conditions import ConditionName
from character.constants.feats import FeatName, FeatType
from character.constants.species import SpeciesName, SpeciesTraitName
from character.models.abilities import Ability, AbilityType
from character.models.character import Character
from character.models.classes import (
    CharacterClass,
    CharacterFeature,
    Class,
    ClassFeature,
)
from character.models.conditions import CharacterCondition, Condition
from character.models.feats import CharacterFeat, Feat
from character.models.species import Species, SpeciesTrait


class AbilityTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AbilityType
        django_get_or_create = ("name",)

    name = factory.Faker("enum", enum_cls=AbilityName)


class AbilityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ability

    ability_type = factory.SubFactory(AbilityTypeFactory)
    score = factory.Faker("random_int")
    modifier = factory.Faker("random_int", min=-5, max=5)


class SpeciesTraitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpeciesTrait
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=SpeciesTraitName)
    description = factory.Faker("text", max_nb_chars=200)


class SpeciesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Species
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=SpeciesName)
    size = "M"
    speed = 30
    darkvision = 0


class CharacterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Character
        django_get_or_create = ("user",)

    name = factory.Sequence(lambda n: f"character{n}")
    user = factory.SubFactory("user.tests.factories.UserFactory")
    species = factory.SubFactory(SpeciesFactory)
    background = factory.Faker("enum", enum_cls=Background)
    xp = factory.Faker("random_int")
    inventory = factory.SubFactory(InventoryFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        character = model_class(*args, **kwargs)
        character.save()
        for ability_name, _ in AbilityName.choices:
            ability = AbilityFactory(ability_type__name=ability_name)
            character.abilities.add(ability)
        return character


class ConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Condition
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=ConditionName)
    description = factory.Faker("text", max_nb_chars=200)


class CharacterConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CharacterCondition

    character = factory.SubFactory(CharacterFactory)
    condition = factory.SubFactory(ConditionFactory)


class FeatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feat
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=FeatName)
    feat_type = FeatType.ORIGIN
    description = factory.Faker("text", max_nb_chars=200)


class CharacterFeatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CharacterFeat

    character = factory.SubFactory(CharacterFactory)
    feat = factory.SubFactory(FeatFactory)
    granted_by = "background"


class ClassFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Class
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=ClassName)
    description = factory.Faker("text", max_nb_chars=200)
    hit_die = 10
    hp_first_level = 10
    hp_higher_levels = 6
    primary_ability = factory.SubFactory(AbilityTypeFactory, name="STR")
    armor_proficiencies = factory.LazyFunction(list)
    weapon_proficiencies = factory.LazyFunction(list)
    starting_wealth_dice = "5d4"


class ClassFeatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClassFeature

    name = factory.Faker("word")
    klass = factory.SubFactory(ClassFactory)
    level = 1
    description = factory.Faker("text", max_nb_chars=500)


class CharacterClassFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CharacterClass

    character = factory.SubFactory(CharacterFactory)
    klass = factory.SubFactory(ClassFactory)
    level = 1
    is_primary = True


class CharacterFeatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CharacterFeature

    character = factory.SubFactory(CharacterFactory)
    class_feature = factory.SubFactory(ClassFeatureFactory)
    source_class = factory.SubFactory(ClassFactory)
    level_gained = 1
