import pytest
from django.core.management import call_command
from django.core.management.commands import loaddata

from character.models.classes import Class
from character.models.equipment import Weapon
from character.utils.classes import get_weapon_choices


@pytest.fixture(autouse=True)
def weapons():
    call_command(loaddata.Command(), "character/fixtures/equipment.yaml")


def enum2textchoice(enum):
    return (enum.value, enum.value)


@pytest.mark.django_db
def test_get_weapon_choices_cleric():
    choices = get_weapon_choices(Class.CLERIC)
    assert choices == [
        enum2textchoice(Weapon.Name.MACE),
        enum2textchoice(Weapon.Name.WARHAMMER),
    ]
