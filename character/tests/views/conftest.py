import pytest

from character.models.classes import Klass

from ..factories import CharacterFactory


@pytest.fixture
def character(client):
    c = CharacterFactory(name="user")
    client.force_login(c.user)
    return c


@pytest.fixture
def cleric(client):
    c = CharacterFactory(name="cleric", class_name=Klass.CLERIC)
    client.force_login(c.user)
    return c


@pytest.fixture
def fighter(client):
    c = CharacterFactory(name="fighter", class_name=Klass.FIGHTER)
    client.force_login(c.user)
    return c


@pytest.fixture
def rogue(client):
    c = CharacterFactory(name="rogue", class_name=Klass.ROGUE)
    client.force_login(c.user)
    return c


@pytest.fixture
def wizard(client):
    c = CharacterFactory(name="wizard", class_name=Klass.WIZARD)
    client.force_login(c.user)
    return c
