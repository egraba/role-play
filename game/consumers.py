import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

import character.models as cmodels
import game.models as gmodels


class EventsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.game = await database_sync_to_async(gmodels.Game.objects.get)(id=game_id)
        self.master_user = await database_sync_to_async(User.objects.get)(
            master__game=self.game
        )
        self.player_user = await database_sync_to_async(User.objects.get)(
            character__player__game=self.game, character__user=self.user
        )
        self.character = await database_sync_to_async(cmodels.Character.objects.get)(
            user=self.user
        )

        self.game_group_name = f"events_{self.game.id}"
        await self.channel_layer.group_add(self.game_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.game_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        if self.master_user == self.user:
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    "type": "master_instruction",
                    "content": message,
                },
            )
        else:
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    "type": "player_choice",
                    "selection": message,
                },
            )

    async def master_instruction(self, event):
        message = "the Master said: "
        content = event["content"]
        await database_sync_to_async(gmodels.Instruction.objects.create)(
            game=self.game,
            message=message,
            content=content,
        )
        await self.send(text_data=json.dumps(event))

    async def player_choice(self, event):
        message = f"[{self.player_user}] said: "
        selection = event["selection"]
        await database_sync_to_async(gmodels.Choice.objects.create)(
            game=self.game,
            message=message,
            character=self.character,
            selection=selection,
        )
        await self.send(text_data=json.dumps(event))
