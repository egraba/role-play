import pytest

from character.models.classes import Class

from ..factories import CharacterFactory


@pytest.fixture
def character(client):
    c = CharacterFactory(name="user")
    client.force_login(c.user)
    return c


@pytest.fixture
def cleric(client):
    c = CharacterFactory(name="cleric", class_name=Class.CLERIC)
    client.force_login(c.user)
    return c


@pytest.fixture
def fighter(client):
    c = CharacterFactory(name="fighter", class_name=Class.FIGHTER)
    client.force_login(c.user)
    return c


@pytest.fixture
def rogue(client):
    c = CharacterFactory(name="rogue", class_name=Class.ROGUE)
    client.force_login(c.user)
    return c


@pytest.fixture
def wizard(client):
    c = CharacterFactory(name="wizard", class_name=Class.WIZARD)
    client.force_login(c.user)
    return c
