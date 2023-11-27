import pytest

from character.models.equipment import Gear, Pack, Weapon
from character.utils.classes.equipment.wizard import WizardEquipmentChoicesProvider


def enum2textchoice(enum):
    return (enum.value, enum.value)


def enum2textchoice_concat(enum1, enum2):
    return (f"{enum1} & {enum2}", f"{enum1} & {enum2}")


@pytest.mark.django_db
def test_get_weapon1_choices(equipment):
    equipment_provider = WizardEquipmentChoicesProvider()
    choices = equipment_provider.get_weapon1_choices()
    assert choices == {
        enum2textchoice(Weapon.Name.QUARTERSTAFF),
        enum2textchoice(Weapon.Name.DAGGER),
    }


@pytest.mark.django_db
def test_get_weapon2_choices(equipment):
    equipment_provider = WizardEquipmentChoicesProvider()
    with pytest.raises(NotImplementedError):
        equipment_provider.get_weapon2_choices()


@pytest.mark.django_db
def test_get_weapon3_choices(equipment):
    equipment_provider = WizardEquipmentChoicesProvider()
    with pytest.raises(NotImplementedError):
        equipment_provider.get_weapon3_choices()


@pytest.mark.django_db
def test_get_armor_choices(equipment):
    equipment_provider = WizardEquipmentChoicesProvider()
    with pytest.raises(NotImplementedError):
        equipment_provider.get_armor_choices()


@pytest.mark.django_db
def test_get_gear_choices(equipment):
    equipment_provider = WizardEquipmentChoicesProvider()
    choices = equipment_provider.get_gear_choices()
    assert choices == {
        enum2textchoice(Gear.Name.COMPONENT_POUCH),
        enum2textchoice(Gear.Name.CRYSTAL),
        enum2textchoice(Gear.Name.ORB),
        enum2textchoice(Gear.Name.ROD),
        enum2textchoice(Gear.Name.STAFF),
        enum2textchoice(Gear.Name.WAND),
    }


@pytest.mark.django_db
def test_get_pack_choices(equipment):
    equipment_provider = WizardEquipmentChoicesProvider()
    choices = equipment_provider.get_pack_choices()
    assert choices == {
        enum2textchoice(Pack.Name.SCHOLARS_PACK),
        enum2textchoice(Pack.Name.EXPLORERS_PACK),
    }
