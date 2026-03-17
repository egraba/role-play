from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from character.tests.factories import CharacterFactory
from user.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_grant_xp_increases_xp():
    out = StringIO()
    user = UserFactory()
    char = CharacterFactory(user=user, xp=0)
    call_command("grant_xp", user.username, "100", stdout=out)
    char.refresh_from_db()
    assert char.xp == 100
    assert "Successfully granted" in out.getvalue()


def test_grant_xp_user_does_not_exist():
    out = StringIO()
    with pytest.raises(CommandError):
        call_command("grant_xp", "nonexistent", "100", stdout=out)


def test_grant_xp_user_has_no_character():
    out = StringIO()
    user = UserFactory()
    with pytest.raises(CommandError):
        call_command("grant_xp", user.username, "100", stdout=out)


def test_grant_xp_invalid_amount():
    out = StringIO()
    user = UserFactory()
    CharacterFactory(user=user)
    with pytest.raises(CommandError):
        call_command("grant_xp", user.username, "0", stdout=out)


def test_grant_xp_negative_amount():
    out = StringIO()
    user = UserFactory()
    CharacterFactory(user=user)
    with pytest.raises(CommandError):
        call_command("grant_xp", user.username, "-1", stdout=out)
