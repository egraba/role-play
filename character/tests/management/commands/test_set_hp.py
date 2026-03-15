from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from character.tests.factories import CharacterFactory
from user.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_set_hp_updates_hp():
    out = StringIO()
    user = UserFactory()
    char = CharacterFactory(user=user)
    call_command("set_hp", user.username, str(char.max_hp - 10), stdout=out)
    char.refresh_from_db()
    assert char.hp == char.max_hp - 10
    assert "Successfully set HP" in out.getvalue()


def test_set_hp_to_zero():
    out = StringIO()
    user = UserFactory()
    CharacterFactory(user=user)
    call_command("set_hp", user.username, "0", stdout=out)


def test_set_hp_exceeds_max_hp():
    out = StringIO()
    user = UserFactory()
    char = CharacterFactory(user=user)
    with pytest.raises(CommandError):
        call_command("set_hp", user.username, str(char.max_hp + 1), stdout=out)


def test_set_hp_negative():
    out = StringIO()
    user = UserFactory()
    CharacterFactory(user=user)
    with pytest.raises(CommandError):
        call_command("set_hp", user.username, "-1", stdout=out)


def test_set_hp_user_does_not_exist():
    out = StringIO()
    with pytest.raises(CommandError):
        call_command("set_hp", "nonexistent", "10", stdout=out)


def test_set_hp_user_has_no_character():
    out = StringIO()
    user = UserFactory()
    with pytest.raises(CommandError):
        call_command("set_hp", user.username, "10", stdout=out)
