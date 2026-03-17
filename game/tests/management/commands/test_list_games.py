from io import StringIO

import pytest
from django.core.management import call_command

from character.tests.factories import CharacterFactory
from game.tests.factories import GameFactory, PlayerFactory
from user.tests.factories import UserFactory

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


def test_list_games_shows_player_count():
    out = StringIO()
    game = GameFactory()
    user = UserFactory()
    char = CharacterFactory(user=user)
    PlayerFactory(user=user, game=game, character=char)
    call_command("list_games", stdout=out)
    # Each output line ends with the player count; game name appears on its line
    output_lines = [line for line in out.getvalue().splitlines() if game.name in line]
    assert len(output_lines) == 1
    assert output_lines[0].strip().endswith("1")
