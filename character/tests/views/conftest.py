import pytest

from character.models.classes import Class

from ..factories import CharacterFactory


@pytest.fixture
def character(client):
    character = CharacterFactory(name="user")
    client.force_login(character.user)
    return character


@pytest.fixture
def cleric(client):
    character = CharacterFactory(name="cleric", class_name=Class.CLERIC)
    client.force_login(character.user)
    return character


@pytest.fixture
def fighter(client):
    character = CharacterFactory(name="fighter", class_name=Class.FIGHTER)
    client.force_login(character.user)
    return character


@pytest.fixture
def rogue(client):
    character = CharacterFactory(name="rogue", class_name=Class.ROGUE)
    client.force_login(character.user)
    return character


@pytest.fixture
def wizard(client):
    character = CharacterFactory(name="wizard", class_name=Class.WIZARD)
    client.force_login(character.user)
    return character
