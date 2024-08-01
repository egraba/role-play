from abc import ABC, abstractmethod

from django.contrib.auth.models import User

from character.models.character import Character
from game.models.game import Game

from .constants.events import RollType
from .tasks import process_roll, store_message
from .schemas import EventSchema


class Command(ABC):
    """
    Generic game command.

    Game commands are executed when events are received by a client.
    In general, the commands are executing asynchronous tasks.
    """

    @abstractmethod
    def execute(self, content: EventSchema, user: User, game: Game) -> None:
        pass


class ProcessMessageCommand(Command):
    def execute(self, content: EventSchema, user: User, game: Game) -> None:
        store_message.delay(
            game_id=game.id,
            date=content["date"],
            message=content["message"],
        )


class CharacterCommandMixin(Command):
    """
    Mixin to inherit from when a command is issued by a character.
    """

    def execute(self, content: EventSchema, user: User, game: Game) -> None:
        try:
            self.character = Character.objects.get(user=user)
        except Character.DoesNotExist as exc:
            exc.add_note(f"Character of user [{user}] not found")
            raise


class AbilityCheckCommand(CharacterCommandMixin):
    def execute(self, content: EventSchema, user: User, game: Game) -> None:
        super().execute(content, user, game)
        process_roll.delay(
            game_id=game.id,
            roll_type=RollType.ABILITY_CHECK,
            date=content["date"],
            character_id=self.character.id,
            message=content["message"],
        )


class SavingThrowCommand(CharacterCommandMixin):
    def execute(self, content: EventSchema, user: User, game: Game) -> None:
        super().execute(content, user, game)
        process_roll.delay(
            game_id=game.id,
            roll_type=RollType.SAVING_THROW,
            date=content["date"],
            character_id=self.character.id,
            message=content["message"],
        )
