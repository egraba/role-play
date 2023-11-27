import pytest

from character.models.equipment import Armor, Gear, Pack, Weapon
from character.utils.classes.equipment.cleric import ClericEquipmentChoicesProvider


def enum2textchoice(enum):
    return (enum.value, enum.value)


def enum2textchoice_concat(enum1, enum2):
    return (f"{enum1} & {enum2}", f"{enum1} & {enum2}")


@pytest.mark.django_db
def test_get_weapon1_choices(equipment):
    equipment_provider = ClericEquipmentChoicesProvider()
    choices = equipment_provider.get_weapon1_choices()
    assert choices == {
        enum2textchoice(Weapon.Name.MACE),
        enum2textchoice(Weapon.Name.WARHAMMER),
    }


@pytest.mark.django_db
def test_get_weapon2_choices(equipment):
    equipment_provider = ClericEquipmentChoicesProvider()
    choices = equipment_provider.get_weapon2_choices()
    assert choices == {
        enum2textchoice(Weapon.Name.CROSSBOW_LIGHT),
        enum2textchoice(Weapon.Name.CLUB),
        enum2textchoice(Weapon.Name.DAGGER),
        enum2textchoice(Weapon.Name.GREATCLUB),
        enum2textchoice(Weapon.Name.HANDAXE),
        enum2textchoice(Weapon.Name.JAVELIN),
        enum2textchoice(Weapon.Name.LIGHT_HAMMER),
        enum2textchoice(Weapon.Name.MACE),
        enum2textchoice(Weapon.Name.QUARTERSTAFF),
        enum2textchoice(Weapon.Name.SICKLE),
        enum2textchoice(Weapon.Name.SPEAR),
        enum2textchoice(Weapon.Name.DART),
        enum2textchoice(Weapon.Name.SHORTBOW),
        enum2textchoice(Weapon.Name.SLING),
    }


@pytest.mark.django_db
def test_get_weapon3_choices(equipment):
    equipment_provider = ClericEquipmentChoicesProvider()
    with pytest.raises(NotImplementedError):
        equipment_provider.get_weapon3_choices()


@pytest.mark.django_db
def test_get_armor_choices(equipment):
    equipment_provider = ClericEquipmentChoicesProvider()
    choices = equipment_provider.get_armor_choices()
    assert choices == {
        enum2textchoice(Armor.Name.SCALE_MAIL),
        enum2textchoice(Armor.Name.LEATHER),
        enum2textchoice(Armor.Name.CHAIN_MAIL),
    }


@pytest.mark.django_db
def test_get_gear_choices(equipment):
    equipment_provider = ClericEquipmentChoicesProvider()
    choices = equipment_provider.get_gear_choices()
    assert choices == {
        enum2textchoice(Gear.Name.AMULET),
        enum2textchoice(Gear.Name.EMBLEM),
        enum2textchoice(Gear.Name.RELIQUARY),
    }


@pytest.mark.django_db
def test_get_pack_choices(equipment):
    equipment_provider = ClericEquipmentChoicesProvider()
    choices = equipment_provider.get_pack_choices()
    assert choices == {
        enum2textchoice(Pack.Name.PRIESTS_PACK),
        enum2textchoice(Pack.Name.EXPLORERS_PACK),
    }
