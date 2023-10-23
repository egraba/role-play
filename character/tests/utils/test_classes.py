import pytest
from django.core.management import call_command
from django.core.management.commands import loaddata

from character.models.classes import Class
from character.models.equipment import Armor, Pack, Weapon
from character.utils.classes import (
    get_armor_choices,
    get_pack_choices,
    get_weapon_choices,
)


@pytest.fixture(autouse=True)
def weapons():
    call_command(loaddata.Command(), "character/fixtures/equipment.yaml")


def enum2textchoice(enum):
    return (enum.value, enum.value)


@pytest.mark.django_db
def test_get_weapon_choices_cleric():
    choices = get_weapon_choices(Class.CLERIC)
    assert choices == {
        enum2textchoice(Weapon.Name.MACE),
        enum2textchoice(Weapon.Name.WARHAMMER),
    }


@pytest.mark.django_db
def test_get_weapon_choices_rogue():
    choices = get_weapon_choices(Class.ROGUE)
    assert choices == {
        enum2textchoice(Weapon.Name.RAPIER),
        enum2textchoice(Weapon.Name.SHORTSWORD),
    }


@pytest.mark.django_db
def test_get_weapon_choices_wizard():
    choices = get_weapon_choices(Class.WIZARD)
    assert choices == {
        enum2textchoice(Weapon.Name.QUARTERSTAFF),
        enum2textchoice(Weapon.Name.DAGGER),
    }


@pytest.mark.django_db
def test_get_armor_choices_cleric():
    choices = get_armor_choices(Class.CLERIC)
    assert choices == {
        enum2textchoice(Armor.Name.SCALE_MAIL),
        enum2textchoice(Armor.Name.LEATHER),
        enum2textchoice(Armor.Name.CHAIN_MAIL),
    }


@pytest.mark.django_db
def test_get_pack_choices_cleric():
    choices = get_pack_choices(Class.CLERIC)
    assert choices == {
        enum2textchoice(Pack.Name.PRIESTS_PACK),
        enum2textchoice(Pack.Name.EXPLORERS_PACK),
    }


@pytest.mark.django_db
def test_get_pack_choices_fighter():
    choices = get_pack_choices(Class.FIGHTER)
    assert choices == {
        enum2textchoice(Pack.Name.DUNGEONEERS_PACK),
        enum2textchoice(Pack.Name.EXPLORERS_PACK),
    }


@pytest.mark.django_db
def test_get_pack_choices_rogue():
    choices = get_pack_choices(Class.ROGUE)
    assert choices == {
        enum2textchoice(Pack.Name.BURGLARS_PACK),
        enum2textchoice(Pack.Name.DUNGEONEERS_PACK),
        enum2textchoice(Pack.Name.EXPLORERS_PACK),
    }


@pytest.mark.django_db
def test_get_pack_choices_wizard():
    choices = get_pack_choices(Class.WIZARD)
    assert choices == {
        enum2textchoice(Pack.Name.SCHOLARS_PACK),
        enum2textchoice(Pack.Name.EXPLORERS_PACK),
    }
