from abc import abstractmethod

from .models.events import Message, RollResponse, CombatInitiativeResponse
from .models.game import Game, Player, Character
from .schemas import EventSchema, PlayerType


class Enricher:
    """
    Enricher class.

    To have a better speed, event messages need to be enriched before the events are
    actually stored in the database.

    Attributes:
        game (Game): Current game instance.
        content (EventSchema): content to enrich.
    """

    def __init__(self, game: Game, content: EventSchema, *args, **kwargs):
        self.game = game
        self.content = content

    @abstractmethod
    def enrich(self):
        """Enrich event messages."""
        pass


class MessageEnricher(Enricher):
    def enrich(self):
        if self.content["player_type"] == PlayerType.MASTER:
            is_from_master = True
            author = None
        else:
            is_from_master = False
            author = Player.objects.get(
                character__user__username=self.content["username"]
            )
        self.content["message"] = Message(
            game=self.game,
            date=self.content["date"],
            content=self.content["message"],
            is_from_master=is_from_master,
            author=author,
        ).get_message()


class RollResponseEnricher(Enricher):
    def enrich(self):
        character = Character.objects.get(user__username=self.content["username"])
        self.content["message"] = RollResponse(
            game=self.game,
            date=self.content["date"],
            character=character,
        ).get_message()


class CombatInitiativeResponseEnricher(Enricher):
    def enrich(self):
        character = Character.objects.get(user__username=self.content["username"])
        self.content["message"] = CombatInitiativeResponse(
            game=self.game,
            date=self.content["date"],
            character=character,
        ).get_message()
