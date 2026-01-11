import pytest

from character.constants.classes import ClassName
from character.models.classes import CharacterClass, Class

from ..factories import CharacterFactory


@pytest.fixture
def character(client):
    c = CharacterFactory(name="user")
    client.force_login(c.user)
    return c


def _create_character_with_class(client, name: str, class_name: str):
    """Helper to create a character with a class association."""
    c = CharacterFactory(name=name)
    klass = Class.objects.get(name=class_name)
    CharacterClass.objects.create(character=c, klass=klass, level=1, is_primary=True)
    client.force_login(c.user)
    return c


@pytest.fixture
def cleric(client):
    return _create_character_with_class(client, "cleric", ClassName.CLERIC)


@pytest.fixture
def fighter(client):
    return _create_character_with_class(client, "fighter", ClassName.FIGHTER)


@pytest.fixture
def rogue(client):
    return _create_character_with_class(client, "rogue", ClassName.ROGUE)


@pytest.fixture
def wizard(client):
    return _create_character_with_class(client, "wizard", ClassName.WIZARD)
