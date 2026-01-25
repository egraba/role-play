import pytest
from django.utils import timezone
from unittest.mock import patch

from character.models.character import Character

from game.models.game import Actor
from game.services import GameEventService

from .factories import GameFactory, PlayerFactory


pytestmark = pytest.mark.django_db


class TestGetAuthor:
    def test_get_author_returns_master_actor(self):
        game = GameFactory()
        user = game.master.user

        author = GameEventService.get_author(game, user)

        assert author == game.master

    def test_get_author_returns_player_actor(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        user = player.user

        author = GameEventService.get_author(game, user)

        assert author == player

    def test_get_author_raises_when_user_not_in_game(self):
        game = GameFactory()
        other_game = GameFactory()
        user = other_game.master.user

        with pytest.raises(Actor.DoesNotExist):
            GameEventService.get_author(game, user)


class TestCreateMessage:
    def test_create_message_saves_to_database(self):
        game = GameFactory()
        user = game.master.user
        content = "Hello, world!"
        date = timezone.now()

        with patch("game.services.send_to_channel") as mock_send:
            message = GameEventService.create_message(
                game=game,
                user=user,
                content=content,
                date=date,
            )

        assert message.id is not None
        assert message.game == game
        assert message.author_id == game.master.actor_ptr_id
        assert message.content == content
        mock_send.assert_called_once_with(message)

    def test_create_message_from_player(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        user = player.user
        content = "Player message"
        date = timezone.now()

        with patch("game.services.send_to_channel") as mock_send:
            message = GameEventService.create_message(
                game=game,
                user=user,
                content=content,
                date=date,
            )

        assert message.author_id == player.actor_ptr_id
        mock_send.assert_called_once()

    def test_create_message_broadcasts_to_channel(self):
        game = GameFactory()
        user = game.master.user
        content = "Test message"
        date = timezone.now()

        with patch("game.services.send_to_channel") as mock_send:
            message = GameEventService.create_message(
                game=game,
                user=user,
                content=content,
                date=date,
            )

            mock_send.assert_called_once_with(message)


class TestGetCharacter:
    def test_get_character_returns_character(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        user = player.character.user

        character = GameEventService.get_character(user)

        assert character == player.character

    def test_get_character_raises_when_no_character(self):
        game = GameFactory()
        user = game.master.user

        with pytest.raises(Character.DoesNotExist):
            GameEventService.get_character(user)


class TestGetPlayer:
    def test_get_player_returns_player(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        user = player.user

        result = GameEventService.get_player(game, user)

        assert result == player

    def test_get_player_raises_when_not_in_game(self):
        game = GameFactory()
        other_game = GameFactory()
        player = PlayerFactory(game=other_game)
        user = player.user

        from game.models.game import Player

        with pytest.raises(Player.DoesNotExist):
            GameEventService.get_player(game, user)
