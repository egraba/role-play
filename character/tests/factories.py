import factory

from character.models.abilities import Ability, AbilityScoreIncrease, AbilityType
from character.models.character import Character
from character.models.classes import Class
from character.models.equipment import Equipment
from character.models.races import Alignment, Race, RacialTrait, Size


class AbilityTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AbilityType
        django_get_or_create = ("name",)

    name = factory.Faker("enum", enum_cls=AbilityType.Name)


class AbilityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ability

    ability_type = factory.SubFactory(AbilityTypeFactory)
    score = factory.Faker("random_int")


class RacialTraitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RacialTrait
        django_get_or_create = ("race",)

    race = factory.Faker("enum", enum_cls=Race)
    adult_age = factory.Faker("random_int")
    life_expectancy = factory.Faker("random_int")
    alignment = factory.Faker("enum", enum_cls=Alignment)
    size = factory.Faker("enum", enum_cls=Size)
    speed = factory.Faker("random_int")


class AbilityScoreIncreaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AbilityScoreIncrease

    racial_trait = factory.SubFactory(RacialTraitFactory)
    ability_type = factory.SubFactory(AbilityTypeFactory)
    increase = factory.Faker("random_int")


class CharacterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Character
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"character{n}")
    user = factory.SubFactory("utils.factories.UserFactory")
    race = factory.Faker("enum", enum_cls=Race)
    class_name = factory.Faker("enum", enum_cls=Class)
    xp = factory.Faker("random_int")


class EquipmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Equipment
        django_get_or_create = ("name",)

    name = factory.Faker("word")
