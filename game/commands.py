from abc import ABC, abstractmethod
from datetime import datetime

from django.contrib.auth.models import User

from character.models.character import Character
from game.models.game import Game

from .constants.events import RollType
from .tasks import process_roll


class Command(ABC):
    """Generic game command."""

    @abstractmethod
    def execute(self, date: datetime, message: str, user: User, game: Game) -> None:
        pass


class CharacterCommand(Command):
    """Game command issued by a character."""

    def execute(self, date: datetime, message: str, user: User, game: Game) -> None:
        try:
            self.character = Character.objects.get(user=user)
        except Character.DoesNotExist:
            raise


class AbilityCheckCommand(CharacterCommand):
    def execute(self, date: datetime, message: str, user: User, game: Game) -> None:
        super().execute(date, message, user, game)
        process_roll.delay(
            game_id=game.id,
            roll_type=RollType.ABILITY_CHECK,
            date=date,
            character_id=self.character.id,
            message=message,
        )


class SavingThrowCommand(CharacterCommand):
    def execute(self, date: datetime, message: str, user: User, game: Game) -> None:
        super().execute(date, message, user, game)
        process_roll.delay(
            game_id=game.id,
            roll_type=RollType.SAVING_THROW,
            date=date,
            character_id=self.character.id,
            message=message,
        )
