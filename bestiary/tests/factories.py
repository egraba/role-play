import factory

from bestiary.constants.monsters import (
    ActionType,
    Alignment,
    ChallengeRating,
    CreatureSize,
    CreatureType,
    DamageRelationType,
    DamageType,
    MonsterName,
    MovementType,
    SenseType,
)
from bestiary.models.monsters import (
    LairActionTemplate,
    LegendaryActionTemplate,
    Monster,
    MonsterActionTemplate,
    MonsterConditionImmunity,
    MonsterDamageRelation,
    MonsterLanguage,
    MonsterMultiattack,
    MonsterReaction,
    MonsterSavingThrow,
    MonsterSense,
    MonsterSettings,
    MonsterSkill,
    MonsterSpeed,
    MonsterTrait,
    MultiattackAction,
)


class MonsterSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterSettings
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=MonsterName)
    size = CreatureSize.MEDIUM
    creature_type = CreatureType.HUMANOID
    alignment = Alignment.TRUE_NEUTRAL
    ac = 10
    hit_dice = "1d8"
    hp_average = 4
    passive_perception = 10
    strength = 10
    dexterity = 10
    constitution = 10
    intelligence = 10
    wisdom = 10
    charisma = 10
    challenge_rating = ChallengeRating.CR_0
    proficiency_bonus = 2


class MonsterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Monster

    settings = factory.SubFactory(MonsterSettingsFactory)
    hp_current = factory.LazyAttribute(lambda o: o.settings.hp_average)
    hp_max = factory.LazyAttribute(lambda o: o.settings.hp_average)


class MonsterActionTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterActionTemplate

    monster = factory.SubFactory(MonsterSettingsFactory)
    name = factory.Sequence(lambda n: f"Action {n}")
    action_type = ActionType.MELEE_WEAPON
    attack_bonus = 5
    reach = 5
    targets = "one target"
    damage_dice = "1d8+3"
    damage_type = DamageType.SLASHING


class MonsterMultiattackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterMultiattack

    monster = factory.SubFactory(MonsterSettingsFactory)
    description = "The creature makes two attacks."


class MultiattackActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MultiattackAction

    multiattack = factory.SubFactory(MonsterMultiattackFactory)
    action = factory.SubFactory(MonsterActionTemplateFactory)
    count = 2


class LegendaryActionTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LegendaryActionTemplate

    monster = factory.SubFactory(MonsterSettingsFactory)
    name = factory.Sequence(lambda n: f"Legendary Action {n}")
    description = "The creature performs a legendary action."
    cost = 1


class LairActionTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LairActionTemplate

    monster = factory.SubFactory(MonsterSettingsFactory)
    description = "A lair effect occurs."


class MonsterTraitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterTrait

    monster = factory.SubFactory(MonsterSettingsFactory)
    name = factory.Sequence(lambda n: f"Trait {n}")
    description = "This creature has a special trait."


class MonsterReactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterReaction

    monster = factory.SubFactory(MonsterSettingsFactory)
    name = factory.Sequence(lambda n: f"Reaction {n}")
    description = "The creature reacts."
    trigger = "When attacked"


class MonsterSpeedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterSpeed

    monster = factory.SubFactory(MonsterSettingsFactory)
    movement_type = MovementType.WALK
    feet = 30


class MonsterSavingThrowFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterSavingThrow

    monster = factory.SubFactory(MonsterSettingsFactory)
    ability = "STR"
    bonus = 5


class MonsterSkillFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterSkill

    monster = factory.SubFactory(MonsterSettingsFactory)
    skill = "Perception"
    bonus = 3


class MonsterSenseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterSense

    monster = factory.SubFactory(MonsterSettingsFactory)
    sense_type = SenseType.DARKVISION
    range_feet = 60


class MonsterDamageRelationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterDamageRelation

    monster = factory.SubFactory(MonsterSettingsFactory)
    damage_type = DamageType.FIRE
    relation_type = DamageRelationType.IMMUNITY


class MonsterConditionImmunityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterConditionImmunity

    monster = factory.SubFactory(MonsterSettingsFactory)
    condition = "poisoned"


class MonsterLanguageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterLanguage

    monster = factory.SubFactory(MonsterSettingsFactory)
    language = "Common"
