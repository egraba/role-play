from character.models.abilities import AbilityType
from character.models.classes import Class
from character.utils.proficiencies import get_saving_throws


def test_saving_throws_cleric():
    assert get_saving_throws(Class.CLERIC) == {
        AbilityType.Name.WISDOM,
        AbilityType.Name.CHARISMA,
    }


def test_saving_throws_figher():
    assert get_saving_throws(Class.FIGHTER) == {
        AbilityType.Name.STRENGTH,
        AbilityType.Name.CONSTITUTION,
    }


def test_saving_throws_rogue():
    assert get_saving_throws(Class.ROGUE) == {
        AbilityType.Name.DEXTERITY,
        AbilityType.Name.INTELLIGENCE,
    }


def test_saving_throws_wizard():
    assert get_saving_throws(Class.WIZARD) == {
        AbilityType.Name.INTELLIGENCE,
        AbilityType.Name.WISDOM,
    }
