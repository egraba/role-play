from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from pydantic import ValidationError

from character.models.character import Character

from .constants.events import RollType
from .exceptions import EventSchemaValidationError
from .models.game import Game
from .schemas import EventOrigin, EventSchema, EventType
from .services import GameEventService


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
            self.game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            self.close(reason=f"Game of {game_id=} not found")
            return
        self.game_group_name = f"game_{self.game.id}_events"
        async_to_sync(self.channel_layer.group_add)(
            self.game_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, code=None):
        if "game_group_name" in self.__dict__:
            async_to_sync(self.channel_layer.group_discard)(
                self.game_group_name, self.channel_name
            )

    def receive_json(self, content, **kwargs):
        try:
            EventSchema(**content)
        except ValidationError as exc:
            raise EventSchemaValidationError(exc.errors()) from exc

        # Server-side events are already processed, just forward to group
        if content.get("origin") == EventOrigin.SERVER_SIDE:
            async_to_sync(self.channel_layer.group_send)(self.game_group_name, content)
            return

        # Client-side events: save to DB first, then broadcast
        match content["type"]:
            case EventType.MESSAGE:
                # Service saves to DB and broadcasts via send_to_channel
                GameEventService.create_message(
                    game=self.game,
                    user=self.user,
                    content=content["message"],
                    date=content["date"],
                )
                return  # Service handles broadcast

            case EventType.ABILITY_CHECK_RESPONSE:
                try:
                    character = GameEventService.get_character(self.user)
                except Character.DoesNotExist:
                    self.close(reason="Character not found")
                    return
                GameEventService.process_roll(
                    game=self.game,
                    player=character.player,
                    date=content["date"],
                    roll_type=RollType.ABILITY_CHECK,
                )
                return  # Service handles broadcast

            case EventType.SAVING_THROW_RESPONSE:
                try:
                    character = GameEventService.get_character(self.user)
                except Character.DoesNotExist:
                    self.close(reason="Character not found")
                    return
                GameEventService.process_roll(
                    game=self.game,
                    player=character.player,
                    date=content["date"],
                    roll_type=RollType.SAVING_THROW,
                )
                return  # Service handles broadcast

            case EventType.COMBAT_INITIATIVE_RESPONSE:
                try:
                    character = GameEventService.get_character(self.user)
                except Character.DoesNotExist:
                    self.close(reason="Character not found")
                    return
                GameEventService.process_combat_initiative_roll(
                    game=self.game,
                    player=character.player,
                    date=content["date"],
                )
                return  # Service handles broadcast

            case _:
                # For unhandled client events, forward to group
                async_to_sync(self.channel_layer.group_send)(
                    self.game_group_name, content
                )

    def __getattr__(self, name: str):
        """Catch-all for Django Channels event dispatch.

        Channels converts event type dots to underscores and calls
        the resulting method (e.g., "game.start" -> "game_start").
        All handlers just forward via send_json, so we use __getattr__
        instead of defining 37 identical methods.
        """
        if name.startswith("_") or name[0].isupper():
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

        def _forward_event(event):
            self.send_json(event)

        return _forward_event
