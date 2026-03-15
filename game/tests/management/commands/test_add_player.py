from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from character.tests.factories import CharacterFactory
from game.models.game import Player
from game.tests.factories import GameFactory
from user.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_add_player_success():
    out = StringIO()
    game = GameFactory()
    user = UserFactory()
    CharacterFactory(user=user)
    call_command("add_player", game.id, user.username, stdout=out)
    assert Player.objects.filter(user=user, game=game).exists()
    assert "Successfully added player" in out.getvalue()
    assert user.username in out.getvalue()
    assert str(game.id) in out.getvalue()


def test_add_player_game_does_not_exist():
    out = StringIO()
    user = UserFactory()
    with pytest.raises(CommandError):
        call_command("add_player", 99999, user.username, stdout=out)


def test_add_player_user_does_not_exist():
    out = StringIO()
    game = GameFactory()
    with pytest.raises(CommandError):
        call_command("add_player", game.id, "nonexistent", stdout=out)


def test_add_player_user_has_no_character():
    out = StringIO()
    game = GameFactory()
    user = UserFactory()
    with pytest.raises(CommandError):
        call_command("add_player", game.id, user.username, stdout=out)


def test_add_player_already_a_player():
    out = StringIO()
    game = GameFactory()
    user = UserFactory()
    char = CharacterFactory(user=user)
    Player.objects.create(user=user, game=game, character=char)
    with pytest.raises(CommandError):
        call_command("add_player", game.id, user.username, stdout=out)
    assert Player.objects.count() == 1
