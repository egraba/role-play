from io import StringIO

import pytest
from django.core.management import call_command

from game.tests.factories import GameFactory

pytestmark = pytest.mark.django_db


def test_list_games_shows_game_id():
    out = StringIO()
    game = GameFactory()
    call_command("list_games", stdout=out)
    assert str(game.id) in out.getvalue()


def test_list_games_shows_game_name():
    out = StringIO()
    game = GameFactory()
    call_command("list_games", stdout=out)
    assert game.name in out.getvalue()


def test_list_games_shows_state():
    out = StringIO()
    GameFactory()
    call_command("list_games", stdout=out)
    assert "preparation" in out.getvalue().lower()


def test_list_games_no_games():
    out = StringIO()
    call_command("list_games", stdout=out)
    assert "No games" in out.getvalue()


def test_list_games_shows_master():
    out = StringIO()
    game = GameFactory()
    call_command("list_games", stdout=out)
    assert game.master.user.username in out.getvalue()
