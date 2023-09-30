import dice
from asgiref.sync import async_to_sync
from channels.exceptions import DenyConnection
from channels.generic.websocket import JsonWebsocketConsumer
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

import game.models as gmodels
import game.tasks as tasks
from character.models.character import Character


class GameEventsConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        game_id = self.scope["url_route"]["kwargs"]["game_id"]
        try:
            self.game = cache.get(f"game{game_id}")
            if not self.game:
                self.game = gmodels.Game.objects.get(id=game_id)
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
        date = timezone.now().isoformat()
        match content["type"]:
            case "master.instruction":
                message = "the Master said: "
                tasks.store_master_instruction.delay(
                    game_id=self.game.id,
                    date=date,
                    message=message,
                    content=content["content"],
                )
            case "master.start":
                message = "the game started."
            case "master.quest":
                message = "the Master updated the quest."
            case "player.choice":
                try:
                    character = Character.objects.get(user=self.user)
                except ObjectDoesNotExist:
                    raise DenyConnection(
                        f"Character of user [{self.user}] not found..."
                    )
                    self.close()
                message = f"[{ self.user }] said: "
                tasks.store_player_choice.delay(
                    game_id=self.game.id,
                    date=date,
                    message=message,
                    character_id=character.id,
                    selection=content["content"],
                )
            case "player.dice.launch":
                try:
                    character = Character.objects.get(user=self.user)
                except ObjectDoesNotExist:
                    raise DenyConnection(
                        f"Character of user [{self.user}] not found..."
                    )
                    self.close()
                message = f"[{ self.user }] launched a dice: "
                score = int(dice.roll("d20"))
                content["content"] = score
                tasks.store_player_dice_launch.delay(
                    game_id=self.game.id,
                    date=date,
                    message=message,
                    character_id=character.id,
                    score=score,
                )
        content.update({"date": date})
        content.update({"message": message})
        async_to_sync(self.channel_layer.group_send)(self.game_group_name, content)

    def master_instruction(self, event):
        self.send_json(event)

    def master_quest(self, event):
        self.send_json(event)

    def master_start(self, event):
        self.send_json(event)

    def player_choice(self, event):
        self.send_json(event)

    def player_dice_launch(self, event):
        self.send_json(event)
