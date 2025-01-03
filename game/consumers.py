from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.core.cache import cache
from pydantic import ValidationError

from character.models.character import Character

from .commands import (
    AbilityCheckResponseCommand,
    CombatInitiativeResponseCommand,
    ProcessMessageCommand,
    SavingThrowResponseCommand,
)
from .event_enrichers import MessageEnricher, RollResponseEnricher
from .exceptions import EventSchemaValidationError
from .models.game import Game
from .schemas import EventOrigin, EventSchema, EventType
from .utils.cache import game_key


class GameEventsConsumer(JsonWebsocketConsumer):
    """
    GameEventsConsumer class.

    Attributes:
        user (User): Logged user.
        game (Game): Current game instance.
    """

    def connect(self):
        # self.scope is set in parent's connect()
        self.user = self.scope["user"]
        # The game ID has to be retrieved to create a channel.
        # There is one room per game.
        game_id = self.scope["url_route"]["kwargs"]["game_id"]
        try:
            self.game = cache.get_or_set(
                game_key(game_id), Game.objects.get(id=game_id)
            )
        except Game.DoesNotExist:
            self.close(reason=f"Game of {game_id=} not found")
        self.game_group_name = f"game_{self.game.id}_events"
        async_to_sync(self.channel_layer.group_add)(
            self.game_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, code=None):
        async_to_sync(self.channel_layer.group_discard)(
            self.game_group_name, self.channel_name
        )

    def receive_json(self, content, **kwargs):
        try:
            EventSchema(**content)
        except ValidationError as exc:
            raise EventSchemaValidationError(exc.errors()) from exc
        # If the event comes from the server, the related data has already been stored
        # in the database, so the event has just to be sent to the group.
        # If the event comes from the client, the data needs to be stored in the database,
        # when it is received by the server.
        if "origin" in content:
            if content["origin"] == EventOrigin.SERVER_SIDE:
                pass
        else:
            match content["type"]:
                case EventType.MESSAGE:
                    command = ProcessMessageCommand()
                    event_enricher = MessageEnricher(self.game, content)
                case EventType.ABILITY_CHECK_RESPONSE:
                    command = AbilityCheckResponseCommand()
                    event_enricher = RollResponseEnricher(self.game, content)
                case EventType.SAVING_THROW_RESPONSE:
                    command = SavingThrowResponseCommand()
                    event_enricher = RollResponseEnricher(self.game, content)
                case EventType.COMBAT_INITIALIZATION:
                    command = ProcessMessageCommand()
                case EventType.COMBAT_INITIATIVE_RESPONSE:
                    command = CombatInitiativeResponseCommand()
                    event_enricher = RollResponseEnricher(self.game, content)
                case _:
                    pass
            try:
                command.execute(
                    content=content,
                    user=self.user,
                    game=self.game,
                )
            except Character.DoesNotExist:
                self.close(reason="Character not found")
            event_enricher.enrich()
        async_to_sync(self.channel_layer.group_send)(self.game_group_name, content)

    def message(self, event):
        """Message typed by player or master on the keyboard."""
        self.send_json(event)

    def game_start(self, event):
        """Message notifying that the game has started."""
        self.send_json(event)

    def quest_update(self, event):
        """Message notifying that the game's quest has been updated by the master."""
        self.send_json(event)

    def ability_check_request(self, event):
        """Ability check request from the master."""
        self.send_json(event)

    def ability_check_response(self, event):
        """Ability check roll from the player."""
        self.send_json(event)

    def ability_check_result(self, event):
        """Ability check result."""
        self.send_json(event)

    def saving_throw_request(self, event):
        """Saving throw request from the master."""
        self.send_json(event)

    def saving_throw_response(self, event):
        """Saving throw roll from the player."""
        self.send_json(event)

    def saving_throw_result(self, event):
        """Saving throw result."""
        self.send_json(event)

    def combat_initialization(self, event):
        """Combat initialization."""
        self.send_json(event)

    def combat_initiative_request(self, event):
        """
        All players have to perform a dexterity check to determine combat order.
        """
        self.send_json(event)

    def combat_initiative_response(self, event):
        """Dexterity check roll from the player."""
        self.send_json(event)

    def combat_initiative_result(self, event):
        """Dexterity check roll result."""
        self.send_json(event)

    def combat_initialization_complete(self, event):
        """Combat initialization complete."""
        self.send_json(event)
