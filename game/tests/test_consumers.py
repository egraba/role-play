from unittest.mock import ANY

import pytest
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.urls import re_path
from faker import Faker

from character.tests.factories import CharacterFactory
from game.consumers import GameEventsConsumer
from game.models.events import DiceLaunch
from game.schemas import GameEvent, GameEventOrigin, GameEventType, PlayerType

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
    async def test_message_from_master(self):
        communicator = WebsocketCommunicator(
            self.application, f"/events/{self.game.id}/"
        )
        communicator.scope["user"] = self.master_user
        communicator.scope["game_id"] = self.game.id
        connected, _ = await communicator.connect()
        assert connected

        fake = Faker()
        date = fake.date_time().isoformat()
        message = fake.text(100)
        game_event = {
            "type": GameEventType.MESSAGE,
            "player_type": PlayerType.MASTER,
            "date": date,
            "message": message,
        }
        assert GameEvent(**game_event)

        await communicator.send_json_to(game_event)
        response = await communicator.receive_json_from()
        assert response == game_event

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_message_from_player(self):
        communicator = WebsocketCommunicator(
            self.application, f"/events/{self.game.id}/"
        )
        communicator.scope["user"] = self.player_user
        communicator.scope["game_id"] = self.game.id
        connected, _ = await communicator.connect()
        assert connected

        fake = Faker()
        date = fake.date_time().isoformat()
        message = fake.text(100)
        game_event = {
            "type": GameEventType.MESSAGE,
            "player_type": PlayerType.PLAYER,
            "date": date,
            "message": message,
        }
        assert GameEvent(**game_event)

        await communicator.send_json_to(game_event)
        response = await communicator.receive_json_from()
        assert response == game_event

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_quest_update(self):
        communicator = WebsocketCommunicator(
            self.application, f"/events/{self.game.id}/"
        )
        communicator.scope["user"] = self.master_user
        communicator.scope["game_id"] = self.game.id
        connected, _ = await communicator.connect()
        assert connected

        fake = Faker()
        date = fake.date_time().isoformat()
        message = "the Master updated the quest."
        game_event = {
            "type": GameEventType.QUEST_UPDATE,
            "player_type": PlayerType.MASTER,
            "date": date,
            "message": message,
            "origin": GameEventOrigin.SERVER_SIDE,
        }
        assert GameEvent(**game_event)

        await communicator.send_json_to(game_event)
        response = await communicator.receive_json_from()
        assert response == game_event

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_game_start(self):
        communicator = WebsocketCommunicator(
            self.application, f"/events/{self.game.id}/"
        )
        communicator.scope["user"] = self.master_user
        communicator.scope["game_id"] = self.game.id
        connected, _ = await communicator.connect()
        assert connected

        fake = Faker()
        date = fake.date_time().isoformat()
        message = "the game started."
        game_event = {
            "type": GameEventType.GAME_START,
            "player_type": PlayerType.MASTER,
            "date": date,
            "message": message,
            "origin": GameEventOrigin.SERVER_SIDE,
        }
        assert GameEvent(**game_event)

        await communicator.send_json_to(game_event)
        response = await communicator.receive_json_from()
        assert response == game_event

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_ability_check_request(self):
        communicator = WebsocketCommunicator(
            self.application, f"/events/{self.game.id}/"
        )
        communicator.scope["user"] = self.master_user
        communicator.scope["game_id"] = self.game.id
        connected, _ = await communicator.connect()
        assert connected

        fake = Faker()
        date = fake.date_time().isoformat()
        message = fake.text(100)
        game_event = {
            "type": GameEventType.ABILITY_CHECK_REQUEST,
            "player_type": PlayerType.MASTER,
            "date": date,
            "message": message,
            "origin": GameEventOrigin.SERVER_SIDE,
        }
        assert GameEvent(**game_event)

        await communicator.send_json_to(game_event)
        response = await communicator.receive_json_from()
        assert response == game_event

        await communicator.disconnect()

    def get_dice_launch_score(self):
        return DiceLaunch.objects.last()

    @pytest.mark.asyncio
    async def test_dice_launch(self):
        communicator = WebsocketCommunicator(
            self.application, f"/events/{self.game.id}/"
        )
        communicator.scope["user"] = self.player_user
        communicator.scope["game_id"] = self.game.id
        connected, _ = await communicator.connect()
        assert connected

        fake = Faker()
        date = fake.date_time().isoformat()
        message = fake.text(100)
        game_event = {
            "type": GameEventType.DICE_LAUNCH,
            "player_type": PlayerType.PLAYER,
            "date": date,
            "message": message,
        }
        assert GameEvent(**game_event)

        await communicator.send_json_to(game_event)
        response = await communicator.receive_json_from()
        expected_json = {
            "type": GameEventType.DICE_LAUNCH,
            "player_type": PlayerType.PLAYER,
            "date": date,
            "message": ANY,
        }
        assert response == expected_json

        await communicator.disconnect()
