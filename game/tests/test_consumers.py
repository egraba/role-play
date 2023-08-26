from unittest.mock import ANY

from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.urls import re_path

import game.models as gmodels
import utils.testing.factories as utfactories
from game.consumers import GameEventsConsumer


class GameEventsConsumerTest(TransactionTestCase):
    def setUp(self):
        self.game = utfactories.GameFactory(master__user__username="master")
        self.master_user = User.objects.get(username="master")
        character = utfactories.CharacterFactory()
        self.player_user = User.objects.get(character=character)
        self.application = URLRouter(
            [
                re_path(r"^events/(?P<game_id>\w+)/$", GameEventsConsumer.as_asgi()),
            ]
        )

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
                "type": "master.instruction",
                "content": "some content",
            }
        )
        response = await communicator.receive_json_from()
        expected_json = {
            "type": "master.instruction",
            "date": ANY,
            "message": "the Master said: ",
            "content": "some content",
        }
        assert response == expected_json

        await communicator.disconnect()

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
                "type": "master.quest",
                "content": "some content",
            }
        )
        response = await communicator.receive_json_from()
        expected_json = {
            "type": "master.quest",
            "date": ANY,
            "message": "the Master updated the quest.",
            "content": "some content",
        }
        assert response == expected_json

        await communicator.disconnect()

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
                "type": "master.start",
                "content": "some content",
            }
        )
        response = await communicator.receive_json_from()
        expected_json = {
            "type": "master.start",
            "date": ANY,
            "message": "the game started.",
            "content": "some content",
        }
        assert response == expected_json

        await communicator.disconnect()

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
                "type": "player.choice",
                "content": "some content",
            }
        )
        response = await communicator.receive_json_from()
        expected_json = {
            "type": "player.choice",
            "date": ANY,
            "message": f"[{ self.player_user }] said: ",
            "content": "some content",
        }
        assert response == expected_json

        await communicator.disconnect()

    def get_dice_launch_score(self):
        print(gmodels.DiceLaunch.objects.last())
        return gmodels.DiceLaunch.objects.last()

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
                "type": "player.dice.launch",
            }
        )
        response = await communicator.receive_json_from()
        expected_json = {
            "type": "player.dice.launch",
            "date": ANY,
            "message": f"[{ self.player_user }] launched a dice: ",
            "content": ANY,
        }
        assert response == expected_json

        await communicator.disconnect()
