from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from game.models.game import Game, Master, Quest
from user.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_create_game_creates_game():
    out = StringIO()
    user = UserFactory()
    call_command("create_game", user.username, stdout=out)
    assert Game.objects.filter(master__user=user).exists()


def test_create_game_assigns_master():
    out = StringIO()
    user = UserFactory()
    call_command("create_game", user.username, stdout=out)
    game = Game.objects.get(master__user=user)
    assert Master.objects.filter(user=user, game=game).exists()


def test_create_game_user_does_not_exist():
    out = StringIO()
    with pytest.raises(CommandError):
        call_command("create_game", "nonexistent_user", stdout=out)


def test_create_game_creates_quest():
    out = StringIO()
    user = UserFactory()
    call_command("create_game", user.username, stdout=out)
    game = Game.objects.get(master__user=user)
    assert Quest.objects.filter(game=game).exists()


def test_create_game_prints_game_id():
    out = StringIO()
    user = UserFactory()
    call_command("create_game", user.username, stdout=out)
    game = Game.objects.get(master__user=user)
    assert str(game.id) in out.getvalue()
