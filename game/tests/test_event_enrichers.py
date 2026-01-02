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
        }

        enricher = MessageEnricher(game, content, master.user)
        enricher.enrich()

        assert content["message"] == "The Master said: Hello, players!"

    def test_enrich_message_from_player(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        content = {
            "date": timezone.now(),
            "message": "Hello, master!",
        }

        enricher = MessageEnricher(game, content, player.user)
        enricher.enrich()

        assert content["message"] == f"{player} said: Hello, master!"

    def test_enrich_uses_authenticated_user_not_content_username(self):
        """Test that the authenticated user is used, not client-provided username."""
        game = GameFactory()
        master = game.master
        content = {
            "date": timezone.now(),
            "message": "Hello!",
            "username": "malicious_username",  # Client-provided, should be ignored
        }

        enricher = MessageEnricher(game, content, master.user)
        enricher.enrich()

        # Should use authenticated user (master), not content["username"]
        assert content["message"] == "The Master said: Hello!"


class TestRollResponseEnricher:
    def test_enrich_sets_ability_check_message(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        user = player.character.user  # Use character's user (the authenticated user)
        content = {
            "date": timezone.now(),
        }

        enricher = RollResponseEnricher(game, content, user)
        enricher.enrich()

        assert content["message"] == f"{player} performed an ability check!"

    def test_enrich_uses_authenticated_user_not_content_username(self):
        """Test that the authenticated user is used, not client-provided username."""
        game = GameFactory()
        player = PlayerFactory(game=game)
        user = player.character.user
        content = {
            "date": timezone.now(),
            "username": "malicious_username",  # Client-provided, should be ignored
        }

        enricher = RollResponseEnricher(game, content, user)
        enricher.enrich()

        # Should use authenticated user, not content["username"]
        assert content["message"] == f"{player} performed an ability check!"


class TestCombatInitiativeResponseEnricher:
    def test_enrich_sets_dexterity_check_message(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        user = player.character.user  # Use character's user (the authenticated user)
        content = {
            "date": timezone.now(),
        }

        enricher = CombatInitiativeResponseEnricher(game, content, user)
        enricher.enrich()

        assert content["message"] == f"{player.character} performed a dexterity check!"

    def test_enrich_uses_authenticated_user_not_content_username(self):
        """Test that the authenticated user is used, not client-provided username."""
        game = GameFactory()
        player = PlayerFactory(game=game)
        user = player.character.user
        content = {
            "date": timezone.now(),
            "username": "malicious_username",  # Client-provided, should be ignored
        }

        enricher = CombatInitiativeResponseEnricher(game, content, user)
        enricher.enrich()

        # Should use authenticated user, not content["username"]
        assert content["message"] == f"{player.character} performed a dexterity check!"
