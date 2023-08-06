import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

import game.models as gmodels


class EventsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.game_group_name = f"events_{self.game_id}"
        await self.channel_layer.group_add(self.game_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.game_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        now = timezone.now()
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                "type": "game_event",
                "date": now.isoformat(),
                "message": message,
            },
        )

    async def game_event(self, event):
        message = event["message"]
        game = await database_sync_to_async(gmodels.Game.objects.get)(id=self.game_id)
        await database_sync_to_async(gmodels.Event.objects.create)(
            game=game, message=message
        )
        await self.send(text_data=json.dumps(event))
