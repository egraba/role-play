import factory

from character.models.character import Character
from character.models.classes import Class
from character.models.equipment import Equipment
from character.models.races import Race


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
