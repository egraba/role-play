from abc import abstractmethod

from .models.events import Message
from .models.game import Game
from .schemas import EventSchema


class Enricher:
    def __init__(self, game: Game, content: EventSchema, *args, **kwargs):
        self.game = game
        self.content = content

    @abstractmethod
    def enrich(self):
        pass


class MessageEnricher(Enricher):
    def enrich(self):
        self.content["message"] = Message(
            game=self.game,
            date=self.content["date"],
            content=self.content["message"],
            is_from_master=True,
        ).get_message()
