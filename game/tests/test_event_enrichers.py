import pytest
from django.utils import timezone

from game.event_enrichers import (
    CombatInitiativeResponseEnricher,
    MessageEnricher,
    RollResponseEnricher,
)

from .factories import GameFactory, PlayerFactory


pytestmark = pytest.mark.django_db


class TestMessageEnricher:
    def test_enrich_message_from_master(self):
        game = GameFactory()
        master = game.master
        content = {
            "date": timezone.now(),
            "message": "Hello, players!",
            "username": master.user.username,
        }

        enricher = MessageEnricher(game, content)
        enricher.enrich()

        assert content["message"] == "The Master said: Hello, players!"

    def test_enrich_message_from_player(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        content = {
            "date": timezone.now(),
            "message": "Hello, master!",
            "username": player.user.username,
        }

        enricher = MessageEnricher(game, content)
        enricher.enrich()

        assert content["message"] == f"{player} said: Hello, master!"


class TestRollResponseEnricher:
    def test_enrich_sets_ability_check_message(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        content = {
            "date": timezone.now(),
            "username": player.character.user.username,
        }

        enricher = RollResponseEnricher(game, content)
        enricher.enrich()

        assert content["message"] == f"{player} performed an ability check!"


class TestCombatInitiativeResponseEnricher:
    def test_enrich_sets_dexterity_check_message(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        content = {
            "date": timezone.now(),
            "username": player.character.user.username,
        }

        enricher = CombatInitiativeResponseEnricher(game, content)
        enricher.enrich()

        assert content["message"] == f"{player.character} performed a dexterity check!"
