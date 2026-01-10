import factory

from character.constants.abilities import AbilityName
from character.constants.backgrounds import Background
from character.constants.conditions import ConditionName
from character.constants.equipment import (
    ArmorName,
    GearName,
    PackName,
    ToolName,
    WeaponName,
)
from character.constants.species import SpeciesName, SpeciesTraitName
from character.models.abilities import Ability, AbilityType
from character.models.character import Character
from character.models.conditions import CharacterCondition, Condition
from character.models.equipment import (
    Armor,
    ArmorSettings,
    Gear,
    GearSettings,
    Inventory,
    Pack,
    PackSettings,
    Tool,
    ToolSettings,
    Weapon,
    WeaponSettings,
)
from character.models.klasses import Klass
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


class InventoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Inventory


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
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"character{n}")
    user = factory.SubFactory("user.tests.factories.UserFactory")
    species = factory.SubFactory(SpeciesFactory)
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


class ArmorSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ArmorSettings
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=ArmorName)
    cost = factory.Faker("random_int")
    ac = factory.Faker("random_int")
    weight = factory.Faker("random_int")


class ArmorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Armor

    settings = factory.SubFactory(ArmorSettingsFactory)


class WeponSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WeaponSettings
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=WeaponName)


class WeaponFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Weapon

    settings = factory.SubFactory(WeponSettingsFactory)


class PackSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PackSettings
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=PackName)


class PackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Pack

    settings = factory.SubFactory(PackSettingsFactory)


class GearSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GearSettings
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=GearName)


class GearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Gear

    settings = factory.SubFactory(GearSettingsFactory)


class ToolSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ToolSettings
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=ToolName)


class ToolFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tool

    settings = factory.SubFactory(ToolSettingsFactory)


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
