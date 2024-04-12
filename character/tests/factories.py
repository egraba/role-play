import factory

from character.constants.abilities import AbilityName
from character.constants.backgrounds import Background
from character.constants.races import Race
from character.models.abilities import Ability, AbilityType
from character.models.character import Character
from character.models.equipment import ArmorSettings, Inventory
from character.models.klasses import Klass


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


class InventoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Inventory


class CharacterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Character
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"character{n}")
    user = factory.SubFactory("utils.factories.UserFactory")
    race = factory.Faker("enum", enum_cls=Race)
    klass = factory.Faker("enum", enum_cls=Klass)
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


class ArmorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ArmorSettings
        django_get_or_create = ("name",)

    name = factory.Faker("word")
    cost = factory.Faker("random_int")
    weight = factory.Faker("random_int")
