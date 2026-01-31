import pytest
from django.utils import timezone
from unittest.mock import patch

from character.models.character import Character

from game.models.game import Actor
from game.models.events import DiceRoll
from game.services import DiceRollService, GameEventService

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


class TestDiceRollService:
    def test_create_dice_roll_saves_to_database(self):
        game = GameFactory()
        user = game.master.user

        with patch("game.services.send_to_channel") as mock_send:
            dice_roll = DiceRollService.create_dice_roll(
                game=game,
                user=user,
                dice_notation="2d6",
                dice_type=6,
                num_dice=2,
                modifier=3,
                individual_rolls=[4, 5],
                total=12,
                roll_purpose="Damage roll",
            )

        assert dice_roll.id is not None
        assert dice_roll.game == game
        assert dice_roll.dice_notation == "2d6"
        assert dice_roll.dice_type == 6
        assert dice_roll.num_dice == 2
        assert dice_roll.modifier == 3
        assert dice_roll.individual_rolls == [4, 5]
        assert dice_roll.total == 12
        assert dice_roll.roll_purpose == "Damage roll"
        mock_send.assert_called_once_with(dice_roll)

    def test_create_dice_roll_from_player(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        user = player.user

        with patch("game.services.send_to_channel") as mock_send:
            dice_roll = DiceRollService.create_dice_roll(
                game=game,
                user=user,
                dice_notation="1d20",
                dice_type=20,
                num_dice=1,
                modifier=0,
                individual_rolls=[15],
                total=15,
            )

        assert dice_roll.author_id == player.actor_ptr_id
        mock_send.assert_called_once()

    def test_create_dice_roll_broadcasts_to_channel(self):
        game = GameFactory()
        user = game.master.user

        with patch("game.services.send_to_channel") as mock_send:
            dice_roll = DiceRollService.create_dice_roll(
                game=game,
                user=user,
                dice_notation="3d8",
                dice_type=8,
                num_dice=3,
                modifier=-2,
                individual_rolls=[3, 7, 5],
                total=13,
            )

            mock_send.assert_called_once_with(dice_roll)

    def test_create_dice_roll_without_purpose(self):
        game = GameFactory()
        user = game.master.user

        with patch("game.services.send_to_channel"):
            dice_roll = DiceRollService.create_dice_roll(
                game=game,
                user=user,
                dice_notation="1d4",
                dice_type=4,
                num_dice=1,
                modifier=0,
                individual_rolls=[3],
                total=3,
            )

        assert dice_roll.roll_purpose == ""

    def test_create_dice_roll_returns_dice_roll_instance(self):
        game = GameFactory()
        user = game.master.user

        with patch("game.services.send_to_channel"):
            dice_roll = DiceRollService.create_dice_roll(
                game=game,
                user=user,
                dice_notation="1d12",
                dice_type=12,
                num_dice=1,
                modifier=0,
                individual_rolls=[8],
                total=8,
            )

        assert isinstance(dice_roll, DiceRoll)
