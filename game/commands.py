from abc import ABC, abstractmethod
from datetime import datetime

from django.contrib.auth.models import User

from character.models.character import Character
from game.models.game import Game

from .constants.events import RollType
from .tasks import process_roll, store_message


class Command(ABC):
    """
    Generic game command.

    Game commands are executed when events are received by a client.
    In general, the commands are executing asynchronous tasks.
    """

    @abstractmethod
    def execute(self, date: datetime, message: str, user: User, game: Game) -> None:
        pass


class StoreMessageCommand(Command):
    def execute(self, date: datetime, message: str, user: User, game: Game) -> None:
        store_message.delay(
            game_id=game.id,
            date=date,
            message=message,
        )


class CharacterCommandMixin(Command):
    """
    Mixin to inherit from when a command is issued by a character.
    """

    def execute(self, date: datetime, message: str, user: User, game: Game) -> None:
        try:
            self.character = Character.objects.get(user=user)
        except Character.DoesNotExist as exc:
            raise Character.DoesNotExist(
                f"Character of user [{user}] not found"
            ) from exc


class AbilityCheckCommand(CharacterCommandMixin):
    def execute(self, date: datetime, message: str, user: User, game: Game) -> None:
        super().execute(date, message, user, game)
        process_roll.delay(
            game_id=game.id,
            roll_type=RollType.ABILITY_CHECK,
            date=date,
            character_id=self.character.id,
            message=message,
        )


class SavingThrowCommand(CharacterCommandMixin):
    def execute(self, date: datetime, message: str, user: User, game: Game) -> None:
        super().execute(date, message, user, game)
        process_roll.delay(
            game_id=game.id,
            roll_type=RollType.SAVING_THROW,
            date=date,
            character_id=self.character.id,
            message=message,
        )
