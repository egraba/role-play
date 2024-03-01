import pytest

from character.models.klasses import Klass

from ..factories import CharacterFactory


@pytest.fixture
def character(client):
    c = CharacterFactory(name="user")
    client.force_login(c.user)
    return c


@pytest.fixture
def cleric(client):
    c = CharacterFactory(name="cleric", klass=Klass.CLERIC)
    client.force_login(c.user)
    return c


@pytest.fixture
def fighter(client):
    c = CharacterFactory(name="fighter", klass=Klass.FIGHTER)
    client.force_login(c.user)
    return c


@pytest.fixture
def rogue(client):
    c = CharacterFactory(name="rogue", klass=Klass.ROGUE)
    client.force_login(c.user)
    return c


@pytest.fixture
def wizard(client):
    c = CharacterFactory(name="wizard", klass=Klass.WIZARD)
    client.force_login(c.user)
    return c
