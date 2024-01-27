from unittest.mock import ANY

import pytest
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.urls import re_path

from character.tests.factories import CharacterFactory
from game.consumers import GameEventsConsumer
from game.models.events import DiceLaunch
from game.utils.channels import EventType

from .factories import GameFactory


@pytest.mark.django_db(transaction=True)
class TestGameEventsConsumer:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.game = GameFactory(master__user__username="master")
        self.master_user = User.objects.get(username="master")
        character = CharacterFactory()
        self.player_user = User.objects.get(character=character)
        self.application = URLRouter(
            [
                re_path(r"^events/(?P<game_id>\w+)/$", GameEventsConsumer.as_asgi()),
            ]
        )

    @pytest.mark.asyncio
    async def test_master_instruction(self):
        communicator = WebsocketCommunicator(
            self.application, f"/events/{self.game.id}/"
        )
        communicator.scope["user"] = self.master_user
        communicator.scope["game_id"] = self.game.id
        connected, _ = await communicator.connect()
        assert connected

        await communicator.send_json_to(
            {
                "type": EventType.MASTER_INSTRUCTION,
                "content": "some content",
            }
        )
        response = await communicator.receive_json_from()
        expected_json = {
            "type": EventType.MASTER_INSTRUCTION,
            "date": ANY,
            "message": "the Master said: ",
            "content": "some content",
        }
        assert response == expected_json

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_master_quest(self):
        communicator = WebsocketCommunicator(
            self.application, f"/events/{self.game.id}/"
        )
        communicator.scope["user"] = self.master_user
        communicator.scope["game_id"] = self.game.id
        connected, _ = await communicator.connect()
        assert connected

        await communicator.send_json_to(
            {
                "type": EventType.MASTER_QUEST_UPDATE,
                "content": "some content",
            }
        )
        response = await communicator.receive_json_from()
        expected_json = {
            "type": EventType.MASTER_QUEST_UPDATE,
            "date": ANY,
            "message": "the Master updated the quest.",
            "content": "some content",
        }
        assert response == expected_json

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_master_start(self):
        communicator = WebsocketCommunicator(
            self.application, f"/events/{self.game.id}/"
        )
        communicator.scope["user"] = self.master_user
        communicator.scope["game_id"] = self.game.id
        connected, _ = await communicator.connect()
        assert connected

        await communicator.send_json_to(
            {
                "type": EventType.MASTER_GAME_START,
                "content": "some content",
            }
        )
        response = await communicator.receive_json_from()
        expected_json = {
            "type": EventType.MASTER_GAME_START,
            "date": ANY,
            "message": "the game started.",
            "content": "some content",
        }
        assert response == expected_json

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_player_choice(self):
        communicator = WebsocketCommunicator(
            self.application, f"/events/{self.game.id}/"
        )
        communicator.scope["user"] = self.player_user
        communicator.scope["game_id"] = self.game.id
        connected, _ = await communicator.connect()
        assert connected

        await communicator.send_json_to(
            {
                "type": EventType.PLAYER_CHOICE,
                "content": "some content",
            }
        )
        response = await communicator.receive_json_from()
        expected_json = {
            "type": EventType.PLAYER_CHOICE,
            "date": ANY,
            "message": f"[{ self.player_user }] said: ",
            "content": "some content",
        }
        assert response == expected_json

        await communicator.disconnect()

    def get_dice_launch_score(self):
        return DiceLaunch.objects.last()

    @pytest.mark.asyncio
    async def test_player_dice_launch(self):
        communicator = WebsocketCommunicator(
            self.application, f"/events/{self.game.id}/"
        )
        communicator.scope["user"] = self.player_user
        communicator.scope["game_id"] = self.game.id
        connected, _ = await communicator.connect()
        assert connected

        await communicator.send_json_to(
            {
                "type": EventType.PLAYER_DICE_LAUNCH,
            }
        )
        response = await communicator.receive_json_from()
        expected_json = {
            "type": EventType.PLAYER_DICE_LAUNCH,
            "date": ANY,
            "message": f"[{ self.player_user }] launched a dice: ",
            "content": ANY,
        }
        assert response == expected_json

        await communicator.disconnect()
