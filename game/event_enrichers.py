from abc import abstractmethod

from django.db.models import Q

from .models.events import CombatInitiativeResponse, Message, RollResponse
from .models.game import Character, Game, Actor
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
        author = Actor.objects.get(
            Q(master__game=self.game, master__user__username=self.content["username"])
            | Q(player__user__username=self.content["username"])
        )
        self.content["message"] = Message(
            game=self.game,
            author=author,
            date=self.content["date"],
            content=self.content["message"],
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
