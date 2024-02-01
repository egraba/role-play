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
from game.utils.channels import GameEvent, GameEventOrigin, GameEventType, PlayerType

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

        fake = Faker()
        event_date = fake.date_time().isoformat()
        event_message = fake.text(100)
        game_event = {
            "type": GameEventType.MASTER_INSTRUCTION,
            "player_type": PlayerType.MASTER,
            "event_date": event_date,
            "event_message": event_message,
        }
        assert GameEvent(**game_event)

        await communicator.send_json_to(game_event)
        response = await communicator.receive_json_from()
        assert response == game_event

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_master_quest_update(self):
        communicator = WebsocketCommunicator(
            self.application, f"/events/{self.game.id}/"
        )
        communicator.scope["user"] = self.master_user
        communicator.scope["game_id"] = self.game.id
        connected, _ = await communicator.connect()
        assert connected

        fake = Faker()
        event_date = fake.date_time().isoformat()
        event_message = "the Master updated the quest."
        game_event = {
            "type": GameEventType.MASTER_QUEST_UPDATE,
            "player_type": PlayerType.MASTER,
            "event_date": event_date,
            "event_message": event_message,
            "event_origin": GameEventOrigin.SERVER_SIDE,
        }
        assert GameEvent(**game_event)

        await communicator.send_json_to(game_event)
        response = await communicator.receive_json_from()
        assert response == game_event

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_master_game_start(self):
        communicator = WebsocketCommunicator(
            self.application, f"/events/{self.game.id}/"
        )
        communicator.scope["user"] = self.master_user
        communicator.scope["game_id"] = self.game.id
        connected, _ = await communicator.connect()
        assert connected

        fake = Faker()
        event_date = fake.date_time().isoformat()
        event_message = "the game started."
        game_event = {
            "type": GameEventType.MASTER_GAME_START,
            "player_type": PlayerType.MASTER,
            "event_date": event_date,
            "event_message": event_message,
            "event_origin": GameEventOrigin.SERVER_SIDE,
        }
        assert GameEvent(**game_event)

        await communicator.send_json_to(game_event)
        response = await communicator.receive_json_from()
        assert response == game_event

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_master_ability_check_request(self):
        communicator = WebsocketCommunicator(
            self.application, f"/events/{self.game.id}/"
        )
        communicator.scope["user"] = self.master_user
        communicator.scope["game_id"] = self.game.id
        connected, _ = await communicator.connect()
        assert connected

        fake = Faker()
        event_date = fake.date_time().isoformat()
        event_message = fake.text(100)
        game_event = {
            "type": GameEventType.MASTER_ABILITY_CHECK_REQUEST,
            "player_type": PlayerType.MASTER,
            "event_date": event_date,
            "event_message": event_message,
            "event_origin": GameEventOrigin.SERVER_SIDE,
        }
        assert GameEvent(**game_event)

        await communicator.send_json_to(game_event)
        response = await communicator.receive_json_from()
        assert response == game_event

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

        fake = Faker()
        event_date = fake.date_time().isoformat()
        event_message = fake.text(100)
        game_event = {
            "type": GameEventType.PLAYER_CHOICE,
            "player_type": PlayerType.PLAYER,
            "event_date": event_date,
            "event_message": event_message,
        }
        assert GameEvent(**game_event)

        await communicator.send_json_to(game_event)
        response = await communicator.receive_json_from()
        assert response == game_event

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

        fake = Faker()
        event_date = fake.date_time().isoformat()
        event_message = fake.text(100)
        game_event = {
            "type": GameEventType.PLAYER_DICE_LAUNCH,
            "player_type": PlayerType.PLAYER,
            "event_date": event_date,
            "event_message": event_message,
        }
        assert GameEvent(**game_event)

        await communicator.send_json_to(game_event)
        response = await communicator.receive_json_from()
        expected_json = {
            "type": GameEventType.PLAYER_DICE_LAUNCH,
            "player_type": PlayerType.PLAYER,
            "event_date": event_date,
            "event_message": ANY,
        }
        assert response == expected_json

        await communicator.disconnect()
