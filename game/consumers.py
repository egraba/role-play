from asgiref.sync import async_to_sync
from channels.exceptions import DenyConnection
from channels.generic.websocket import JsonWebsocketConsumer
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from character.models.character import Character
from game.models.game import Game
from game.tasks import (
    store_master_instruction,
    store_player_choice,
    store_player_dice_launch,
)
from game.utils.channels import GameEventOrigin, GameEventType
from utils.dice import Dice


class GameEventsConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
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
        # Check the origin of the event.
        #
        # If the event comes from the server, the related data has already been stored
        # in the database, so the event has just to be sent to the group.
        #
        # If the event comes from the client, the data needs to be stored in the database.
        if "origin" in content:
            if content["origin"] == GameEventOrigin.SERVER_SIDE:
                pass

        else:
            date = timezone.now().isoformat()
            content.update({"date": date})

            match content["type"]:
                case GameEventType.MASTER_INSTRUCTION:
                    store_master_instruction.delay(
                        game_id=self.game.id,
                        date=date,
                        event_message=f"the Master said: {content['event_message']}",
                    )
                case GameEventType.PLAYER_CHOICE:
                    try:
                        character = Character.objects.get(user=self.user)
                    except ObjectDoesNotExist:
                        raise DenyConnection(
                            f"Character of user [{self.user}] not found..."
                        )
                        self.close()
                    message = f"[{ self.user }] said: "
                    store_player_choice.delay(
                        game_id=self.game.id,
                        date=date,
                        message=message,
                        character_id=character.id,
                        selection=content["content"],
                    )
                case GameEventType.PLAYER_DICE_LAUNCH:
                    try:
                        character = Character.objects.get(user=self.user)
                    except ObjectDoesNotExist:
                        raise DenyConnection(
                            f"Character of user [{self.user}] not found..."
                        )
                        self.close()
                    message = f"[{ self.user }] launched a dice: "
                    score = Dice("d20").roll()
                    content["content"] = score
                    store_player_dice_launch.delay(
                        game_id=self.game.id,
                        date=date,
                        message=message,
                        character_id=character.id,
                        score=score,
                    )

        async_to_sync(self.channel_layer.group_send)(self.game_group_name, content)

    def master_instruction(self, event):
        self.send_json(event)

    def master_quest_update(self, event):
        self.send_json(event)

    def master_ability_check_request(self, event):
        self.send_json(event)

    def master_game_start(self, event):
        self.send_json(event)

    def player_choice(self, event):
        self.send_json(event)

    def player_dice_launch(self, event):
        self.send_json(event)
