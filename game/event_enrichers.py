from abc import abstractmethod

from .models.events import Message
from .models.game import Game
from .schemas import EventSchema


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
        self.content["message"] = Message(
            game=self.game,
            date=self.content["date"],
            content=self.content["message"],
            is_from_master=True,
        ).get_message()
