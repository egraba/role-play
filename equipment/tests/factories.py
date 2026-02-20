import factory

from equipment.constants.equipment import (
    ArmorName,
    ArmorType,
    GearName,
    PackName,
    ToolName,
    WeaponName,
    WeaponType,
)
from equipment.constants.magic_items import (
    MagicItemName,
    MagicItemType,
    Rarity,
)
from equipment.models.equipment import (
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
from equipment.models.magic_items import (
    Attunement,
    MagicItem,
    MagicItemSettings,
)


class InventoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Inventory


class ArmorSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ArmorSettings
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=ArmorName)
    armor_type = ArmorType.LIGHT_ARMOR
    cost = factory.Faker("random_int")
    ac = factory.Faker("pystr", max_chars=5)
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
    weapon_type = WeaponType.SIMPLE_MELEE
    cost = factory.Faker("random_int")
    damage = factory.Faker("pystr", max_chars=5)
    weight = factory.Faker("random_int")
    properties = ""


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


class MagicItemSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MagicItemSettings
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=MagicItemName)
    item_type = MagicItemType.WONDROUS
    rarity = Rarity.UNCOMMON
    requires_attunement = False
    description = factory.Faker("text", max_nb_chars=200)


class MagicItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MagicItem

    settings = factory.SubFactory(MagicItemSettingsFactory)
    inventory = factory.SubFactory(InventoryFactory)


class AttunementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Attunement

    # Lazy string avoids circular import with character.tests.factories
    character = factory.SubFactory("character.tests.factories.CharacterFactory")
    magic_item = factory.SubFactory(MagicItemFactory)
