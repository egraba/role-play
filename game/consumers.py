from asgiref.sync import async_to_sync
from channels.exceptions import DenyConnection
from channels.generic.websocket import JsonWebsocketConsumer
from django.core.cache import cache

from character.models.character import Character

from .commands import AbilityCheckCommand, SavingThrowCommand, StoreMessageCommand
from .models.game import Game
from .schemas import GameEventOrigin, GameEventType
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
        except Game.DoesNotExist as exc:
            self.close()
            raise DenyConnection(f"Game [{game_id}] not found") from exc
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
        # If the event comes from the server, the related data has already been stored
        # in the database, so the event has just to be sent to the group.
        # If the event comes from the client, the data needs to be stored in the database,
        # when it is received by the server.
        if "origin" in content:
            if content["origin"] == GameEventOrigin.SERVER_SIDE:
                pass
        else:
            match content["type"]:
                case GameEventType.MESSAGE:
                    command = StoreMessageCommand()
                case GameEventType.ABILITY_CHECK:
                    command = AbilityCheckCommand()
                case GameEventType.SAVING_THROW:
                    command = SavingThrowCommand()
                case GameEventType.COMBAT_INITIATION:
                    command = StoreMessageCommand()
                case _:
                    pass
            try:
                command.execute(
                    date=content["date"],
                    message=content["message"],
                    user=self.user,
                    game=self.game,
                )
            except Character.DoesNotExist as exc:
                self.close()
                raise DenyConnection(exc.__traceback__) from exc
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

    def ability_check(self, event):
        """Ability check roll from the player."""
        self.send_json(event)

    def ability_check_result(self, event):
        """Ability check result."""
        self.send_json(event)

    def saving_throw_request(self, event):
        """Saving throw request from the master."""
        self.send_json(event)

    def saving_throw(self, event):
        """Saving throw roll from the player."""
        self.send_json(event)

    def saving_throw_result(self, event):
        """Saving throw result."""
        self.send_json(event)

    def combat_initiation(self, event):
        """Combat initiation."""
        self.send_json(event)
