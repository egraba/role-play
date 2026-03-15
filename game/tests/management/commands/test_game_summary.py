from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from character.tests.factories import CharacterFactory
from game.models.game import Player
from game.tests.factories import GameFactory
from user.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_game_summary_shows_game_name():
    out = StringIO()
    game = GameFactory()
    call_command("game_summary", game.id, stdout=out)
    assert game.name in out.getvalue()


def test_game_summary_shows_master():
    out = StringIO()
    game = GameFactory()
    call_command("game_summary", game.id, stdout=out)
    assert game.master.user.username in out.getvalue()


def test_game_summary_shows_players():
    out = StringIO()
    game = GameFactory()
    user = UserFactory()
    char = CharacterFactory(user=user)
    Player.objects.create(user=user, game=game, character=char)
    call_command("game_summary", game.id, stdout=out)
    assert user.username in out.getvalue()


def test_game_summary_game_does_not_exist():
    out = StringIO()
    with pytest.raises(CommandError):
        call_command("game_summary", 99999, stdout=out)
