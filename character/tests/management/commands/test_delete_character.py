from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from faker import Faker

from character.models.character import Character
from character.tests.factories import CharacterFactory
from utils.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_delete_character_user_exists():
    out = StringIO()
    user = UserFactory()
    call_command("delete_character", user.username, stdout=out)
    assert "Successfully deleted the character" in out.getvalue()


def test_delete_character_user_does_not_exist():
    out = StringIO()
    fake = Faker()
    username = fake.user_name()
    with pytest.raises(CommandError):
        call_command("delete_character", username, stdout=out)


def test_delete_character_character_exists():
    out = StringIO()
    user = UserFactory()
    CharacterFactory(user=user)
    call_command("delete_character", user.username, stdout=out)
    assert "Successfully deleted the character" in out.getvalue()
    assert not Character.objects.filter(user=user).exists()


def test_delete_character_character_does_not_exist():
    out = StringIO()
    user = UserFactory()
    call_command("delete_character", user.username, stdout=out)
    assert "Successfully deleted the character" in out.getvalue()
    assert not Character.objects.filter(user=user).exists()
