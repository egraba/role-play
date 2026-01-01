import pytest
from django.utils import timezone
from unittest.mock import patch

from game.commands import (
    AbilityCheckResponseCommand,
    CombatInitiativeResponseCommand,
    ProcessMessageCommand,
    SavingThrowResponseCommand,
)
from game.constants.events import RollType

from .factories import GameFactory, PlayerFactory


pytestmark = pytest.mark.django_db


class TestProcessMessageCommand:
    def test_execute_calls_store_message_task(self):
        game = GameFactory()
        user = game.master.user
        content = {
            "date": timezone.now(),
            "message": "Hello, world!",
            "username": user.username,
        }

        with patch("game.commands.store_message.delay") as mock_task:
            command = ProcessMessageCommand()
            command.execute(content=content, user=user, game=game)

            mock_task.assert_called_once_with(
                game_id=game.id,
                date=content["date"],
                message=content["message"],
                author_str=content["username"],
            )


class TestAbilityCheckResponseCommand:
    def test_execute_calls_process_roll_task_with_correct_arguments(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        user = player.character.user  # Use character's user, not player's user
        content = {
            "date": timezone.now(),
            "username": user.username,
        }

        with patch("game.commands.process_roll.delay") as mock_task:
            command = AbilityCheckResponseCommand()
            command.execute(content=content, user=user, game=game)

            mock_task.assert_called_once_with(
                game_id=game.id,
                author_id=player.id,
                date=content["date"],
                roll_type=RollType.ABILITY_CHECK,
            )

    def test_execute_raises_exception_when_character_not_found(self):
        game = GameFactory()
        user = game.master.user  # Master doesn't have a character
        content = {
            "date": timezone.now(),
            "username": user.username,
        }

        command = AbilityCheckResponseCommand()
        with pytest.raises(Exception):
            command.execute(content=content, user=user, game=game)


class TestSavingThrowResponseCommand:
    def test_execute_calls_process_roll_task_with_correct_arguments(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        user = player.character.user  # Use character's user, not player's user
        content = {
            "date": timezone.now(),
            "username": user.username,
        }

        with patch("game.commands.process_roll.delay") as mock_task:
            command = SavingThrowResponseCommand()
            command.execute(content=content, user=user, game=game)

            mock_task.assert_called_once_with(
                game_id=game.id,
                author_id=player.id,
                date=content["date"],
                roll_type=RollType.SAVING_THROW,
            )

    def test_execute_raises_exception_when_character_not_found(self):
        game = GameFactory()
        user = game.master.user  # Master doesn't have a character
        content = {
            "date": timezone.now(),
            "username": user.username,
        }

        command = SavingThrowResponseCommand()
        with pytest.raises(Exception):
            command.execute(content=content, user=user, game=game)


class TestCombatInitiativeResponseCommand:
    def test_execute_calls_process_combat_initiative_roll_task_with_correct_arguments(
        self,
    ):
        game = GameFactory()
        player = PlayerFactory(game=game)
        user = player.character.user  # Use character's user, not player's user
        content = {
            "date": timezone.now(),
            "username": user.username,
        }

        with patch("game.commands.process_combat_initiative_roll.delay") as mock_task:
            command = CombatInitiativeResponseCommand()
            command.execute(content=content, user=user, game=game)

            mock_task.assert_called_once_with(
                game_id=game.id,
                player_id=player.id,
                date=content["date"],
            )

    def test_execute_raises_exception_when_character_not_found(self):
        game = GameFactory()
        user = game.master.user  # Master doesn't have a character
        content = {
            "date": timezone.now(),
            "username": user.username,
        }

        command = CombatInitiativeResponseCommand()
        with pytest.raises(Exception):
            command.execute(content=content, user=user, game=game)
