import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

import chat.models as cmodels


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        now = timezone.now()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "user": self.user.username,
                "datetime": now.isoformat(),
            },
        )

    async def chat_message(self, event):
        user = self.user
        content = event["message"]
        room = await database_sync_to_async(cmodels.Room.objects.get)(id=self.room_id)
        await database_sync_to_async(cmodels.Message.objects.create)(
            user=user, content=content, room=room
        )
        await self.send(text_data=json.dumps(event))
