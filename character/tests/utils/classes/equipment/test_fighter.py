import pytest

from character.models.equipment import Armor, Pack, Weapon
from character.utils.classes.equipment.fighter import FighterEquipmentChoicesProvider


def enum2textchoice(enum):
    return (enum.value, enum.value)


def enum2textchoice_concat(enum1, enum2):
    return (f"{enum1} & {enum2}", f"{enum1} & {enum2}")


@pytest.mark.django_db
def test_get_weapon1_choices(equipment):
    equipment_provider = FighterEquipmentChoicesProvider()
    choices = equipment_provider.get_weapon1_choices()
    assert choices == {
        enum2textchoice(Armor.Name.CHAIN_MAIL),
        enum2textchoice_concat(Armor.Name.LEATHER, Weapon.Name.LONGBOW),
    }


@pytest.mark.django_db
def test_get_weapon2_choices(equipment):
    equipment_provider = FighterEquipmentChoicesProvider()
    choices = equipment_provider.get_weapon2_choices()
    assert choices == {
        enum2textchoice(Weapon.Name.BATTLEAXE),
        enum2textchoice(Weapon.Name.FLAIL),
        enum2textchoice(Weapon.Name.GLAIVE),
        enum2textchoice(Weapon.Name.GREATAXE),
        enum2textchoice(Weapon.Name.GREATSWORD),
        enum2textchoice(Weapon.Name.HALBERD),
        enum2textchoice(Weapon.Name.LANCE),
        enum2textchoice(Weapon.Name.LONGSWORD),
        enum2textchoice(Weapon.Name.MAUL),
        enum2textchoice(Weapon.Name.MORNINGSTAR),
        enum2textchoice(Weapon.Name.PIKE),
        enum2textchoice(Weapon.Name.RAPIER),
        enum2textchoice(Weapon.Name.SCIMITAR),
        enum2textchoice(Weapon.Name.SHORTSWORD),
        enum2textchoice(Weapon.Name.TRIDENT),
        enum2textchoice(Weapon.Name.WAR_PICK),
        enum2textchoice(Weapon.Name.WARHAMMER),
        enum2textchoice(Weapon.Name.WHIP),
        enum2textchoice(Weapon.Name.BLOWGUN),
        enum2textchoice(Weapon.Name.CROSSBOW_HAND),
        enum2textchoice(Weapon.Name.CROSSBOW_HEAVY),
        enum2textchoice(Weapon.Name.LONGBOW),
        enum2textchoice(Weapon.Name.NET),
    }


@pytest.mark.django_db
def test_get_weapon3_choices(equipment):
    equipment_provider = FighterEquipmentChoicesProvider()
    choices = equipment_provider.get_weapon3_choices()
    assert choices == {
        enum2textchoice(Weapon.Name.CROSSBOW_LIGHT),
        enum2textchoice(Weapon.Name.HANDAXE),
    }


@pytest.mark.django_db
def test_get_armor_choices(equipment):
    equipment_provider = FighterEquipmentChoicesProvider()
    with pytest.raises(NotImplementedError):
        equipment_provider.get_armor_choices()


@pytest.mark.django_db
def test_get_gear_choices(equipment):
    equipment_provider = FighterEquipmentChoicesProvider()
    with pytest.raises(NotImplementedError):
        equipment_provider.get_gear_choices()


@pytest.mark.django_db
def test_get_pack_choices(equipment):
    equipment_provider = FighterEquipmentChoicesProvider()
    choices = equipment_provider.get_pack_choices()
    assert choices == {
        enum2textchoice(Pack.Name.DUNGEONEERS_PACK),
        enum2textchoice(Pack.Name.EXPLORERS_PACK),
    }
