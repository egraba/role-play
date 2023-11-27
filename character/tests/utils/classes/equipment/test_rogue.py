import pytest

from character.models.equipment import Pack, Weapon
from character.utils.classes.equipment.rogue import RogueEquipmentChoicesProvider


def enum2textchoice(enum):
    return (enum.value, enum.value)


def enum2textchoice_concat(enum1, enum2):
    return (f"{enum1} & {enum2}", f"{enum1} & {enum2}")


@pytest.mark.django_db
def test_get_weapon1_choices(equipment):
    equipment_provider = RogueEquipmentChoicesProvider()
    choices = equipment_provider.get_weapon1_choices()
    assert choices == {
        enum2textchoice(Weapon.Name.RAPIER),
        enum2textchoice(Weapon.Name.SHORTSWORD),
    }


@pytest.mark.django_db
def test_get_weapon2_choices(equipment):
    equipment_provider = RogueEquipmentChoicesProvider()
    choices = equipment_provider.get_weapon2_choices()
    assert choices == {
        enum2textchoice(Weapon.Name.SHORTBOW),
        enum2textchoice(Weapon.Name.SHORTSWORD),
    }


@pytest.mark.django_db
def test_get_weapon3_choices(equipment):
    equipment_provider = RogueEquipmentChoicesProvider()
    with pytest.raises(NotImplementedError):
        equipment_provider.get_weapon3_choices()


@pytest.mark.django_db
def test_get_armor_choices(equipment):
    equipment_provider = RogueEquipmentChoicesProvider()
    with pytest.raises(NotImplementedError):
        equipment_provider.get_armor_choices()


@pytest.mark.django_db
def test_get_gear_choices(equipment):
    equipment_provider = RogueEquipmentChoicesProvider()
    with pytest.raises(NotImplementedError):
        equipment_provider.get_gear_choices()


@pytest.mark.django_db
def test_get_pack_choices(equipment):
    equipment_provider = RogueEquipmentChoicesProvider()
    choices = equipment_provider.get_pack_choices()
    assert choices == {
        enum2textchoice(Pack.Name.BURGLARS_PACK),
        enum2textchoice(Pack.Name.DUNGEONEERS_PACK),
        enum2textchoice(Pack.Name.EXPLORERS_PACK),
    }
