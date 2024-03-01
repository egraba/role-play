import factory

from character.constants.abilities import AbilityName
from character.models.abilities import Ability, AbilityType
from character.models.character import Character
from character.models.klasses import Klass
from character.models.equipment import Equipment
from character.models.races import Race


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


class CharacterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Character
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"character{n}")
    user = factory.SubFactory("utils.factories.UserFactory")
    race = factory.Faker("enum", enum_cls=Race)
    klass = factory.Faker("enum", enum_cls=Klass)
    xp = factory.Faker("random_int")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        character = model_class(*args, **kwargs)
        character.save()
        for ability_name, _ in AbilityName.choices:
            ability = AbilityFactory(ability_type__name=ability_name)
            character.abilities.add(ability)
        return character


class EquipmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Equipment
        django_get_or_create = ("name",)

    name = factory.Faker("word")
