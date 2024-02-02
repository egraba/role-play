from asgiref.sync import async_to_sync
from channels.exceptions import DenyConnection
from channels.generic.websocket import JsonWebsocketConsumer
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from character.models.character import Character
from game.models.game import Game
from game.tasks import process_ability_check, store_message

from .schemas import GameEventOrigin, GameEventType


class GameEventsConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        # The game ID has to be retrieved to create a channel.
        # There is one room per game.
        game_id = self.scope["url_route"]["kwargs"]["game_id"]
        try:
            self.game = cache.get(f"game{game_id}")
            if not self.game:
                self.game = Game.objects.get(id=game_id)
                cache.set(f"game{game_id}", self.game)
        except ObjectDoesNotExist:
            raise DenyConnection(f"Game [{game_id}] not found...")
            self.close()

        self.game_group_name = f"game_{self.game.id}_events"
        async_to_sync(self.channel_layer.group_add)(
            self.game_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.game_group_name, self.channel_name
        )

    def receive_json(self, content):
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
                    store_message.delay(
                        game_id=self.game.id,
                        date=content["date"],
                        message=content["message"],
                    )
                case GameEventType.ABILITY_CHECK:
                    try:
                        character = Character.objects.get(user=self.user)
                    except ObjectDoesNotExist:
                        raise DenyConnection(
                            f"Character of user [{self.user}] not found..."
                        )
                        self.close()
                    process_ability_check.delay(
                        game_id=self.game.id,
                        date=content["date"],
                        character_id=character.id,
                        message=content["message"],
                    )
                case _:
                    pass

        pass

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
