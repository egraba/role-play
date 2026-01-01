from abc import ABC, abstractmethod

from character.models.character import Character
from game.models.game import Game
from user.models import User

from .constants.events import RollType
from .schemas import EventSchema
from .tasks import process_combat_initiative_roll, process_roll, store_message


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
            author_str=content["username"],
        )


class CharacterCommandMixin(Command):
    """
    Mixin to inherit from when a command is issued by a character.
    """

    def execute(self, content: EventSchema, user: User, game: Game) -> None:
        try:
            self.character = Character.objects.get(user=user)
        except Character.DoesNotExist as exc:
            exc.add_note(f"Character of user {user=} not found")
            raise


class AbilityCheckResponseCommand(CharacterCommandMixin):
    def execute(self, content: EventSchema, user: User, game: Game) -> None:
        super().execute(content, user, game)
        process_roll.delay(
            game_id=game.id,
            author_id=self.character.player.id,
            date=content["date"],
            roll_type=RollType.ABILITY_CHECK,
        )


class SavingThrowResponseCommand(CharacterCommandMixin):
    def execute(self, content: EventSchema, user: User, game: Game) -> None:
        super().execute(content, user, game)
        process_roll.delay(
            game_id=game.id,
            author_id=self.character.player.id,
            date=content["date"],
            roll_type=RollType.SAVING_THROW,
        )


class CombatInitiativeResponseCommand(CharacterCommandMixin):
    def execute(self, content: EventSchema, user: User, game: Game) -> None:
        super().execute(content, user, game)
        process_combat_initiative_roll.delay(
            game_id=game.id,
            player_id=self.character.player.id,
            date=content["date"],
        )
