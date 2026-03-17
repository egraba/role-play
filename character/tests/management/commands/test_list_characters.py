from io import StringIO

import pytest
from django.core.management import call_command

from character.tests.factories import CharacterFactory
from user.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_list_characters_shows_username():
    out = StringIO()
    user = UserFactory()
    CharacterFactory(user=user)
    call_command("list_characters", stdout=out)
    assert user.username in out.getvalue()


def test_list_characters_shows_character_name():
    out = StringIO()
    user = UserFactory()
    char = CharacterFactory(user=user)
    call_command("list_characters", stdout=out)
    assert char.name in out.getvalue()


def test_list_characters_shows_hp():
    out = StringIO()
    user = UserFactory()
    char = CharacterFactory(user=user)
    call_command("list_characters", stdout=out)
    output = out.getvalue()
    assert f"{char.hp}/{char.max_hp}" in output


def test_list_characters_shows_species_level_xp():
    out = StringIO()
    user = UserFactory()
    char = CharacterFactory(user=user)
    call_command("list_characters", stdout=out)
    output = out.getvalue()
    assert char.species.name in output
    assert str(char.level) in output
    assert str(char.xp) in output


def test_list_characters_no_characters():
    out = StringIO()
    call_command("list_characters", stdout=out)
    assert "No characters" in out.getvalue()
