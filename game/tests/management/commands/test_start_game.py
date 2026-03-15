from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from game.constants.game import GameState
from game.tests.factories import GameFactory

pytestmark = pytest.mark.django_db


def test_start_game_sets_state_ongoing():
    out = StringIO()
    game = GameFactory()
    call_command("start_game", game.id, stdout=out)
    game.refresh_from_db()
    assert game.state == GameState.ONGOING
    assert "Successfully started game" in out.getvalue()


def test_start_game_sets_start_date():
    from django.utils import timezone

    out = StringIO()
    game = GameFactory()
    before = timezone.now()
    call_command("start_game", game.id, stdout=out)
    game.refresh_from_db()
    assert game.start_date is not None
    assert game.start_date >= before


def test_start_game_does_not_exist():
    out = StringIO()
    with pytest.raises(CommandError):
        call_command("start_game", 99999, stdout=out)


def test_start_game_already_ongoing():
    out = StringIO()
    game = GameFactory(state=GameState.ONGOING)
    with pytest.raises(CommandError):
        call_command("start_game", game.id, stdout=out)
