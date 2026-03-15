from io import StringIO

import pytest
from django.core.management import call_command

from character.models.character import Character
from game.models.game import Game, Master, Player
from user.models import User

pytestmark = pytest.mark.django_db


def test_create_scenario_creates_users():
    out = StringIO()
    call_command("create_scenario", stdout=out)
    assert User.objects.filter(username="thomas").exists()
    assert User.objects.filter(username="eric").exists()
    assert User.objects.filter(username="seb").exists()


def test_create_scenario_creates_characters_for_players_only():
    out = StringIO()
    call_command("create_scenario", stdout=out)
    thomas = User.objects.get(username="thomas")
    eric = User.objects.get(username="eric")
    seb = User.objects.get(username="seb")
    assert not Character.objects.filter(user=thomas).exists()
    assert Character.objects.filter(user=eric).exists()
    assert Character.objects.filter(user=seb).exists()


def test_create_scenario_creates_game():
    out = StringIO()
    call_command("create_scenario", stdout=out)
    assert Game.objects.filter(name="Scenario").exists()


def test_create_scenario_assigns_master():
    out = StringIO()
    call_command("create_scenario", stdout=out)
    thomas = User.objects.get(username="thomas")
    game = Game.objects.get(name="Scenario")
    assert Master.objects.filter(user=thomas, game=game).exists()


def test_create_scenario_assigns_players():
    out = StringIO()
    call_command("create_scenario", stdout=out)
    game = Game.objects.get(name="Scenario")
    eric = User.objects.get(username="eric")
    seb = User.objects.get(username="seb")
    assert Player.objects.filter(user=eric, game=game).exists()
    assert Player.objects.filter(user=seb, game=game).exists()


def test_create_scenario_is_idempotent():
    out = StringIO()
    call_command("create_scenario", stdout=out)
    call_command("create_scenario", stdout=out)
    assert Game.objects.filter(name="Scenario").count() == 1
    assert User.objects.filter(username="eric").count() == 1
    game = Game.objects.get(name="Scenario")
    assert Player.objects.filter(game=game).count() == 2
    assert Master.objects.filter(game=game).count() == 1
    thomas = User.objects.get(username="thomas")
    assert not Character.objects.filter(user=thomas).exists()


def test_create_scenario_success_message():
    out = StringIO()
    call_command("create_scenario", stdout=out)
    assert "Successfully created scenario" in out.getvalue()
