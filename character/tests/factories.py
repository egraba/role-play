import factory

from character.models.equipment import Equipment


class EquipmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Equipment
        django_get_or_create = ("name",)

    name = factory.Faker("word")
