import pytest
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.urls import re_path
from faker import Faker

from character.tests.factories import CharacterFactory
from game.consumers import GameEventsConsumer
from game.schemas import EventSchema, GameEventOrigin, GameEventType, PlayerType

from .factories import GameFactory


@pytest.mark.django_db(transaction=True)
class TestGameEventsConsumer:
    @pytest.fixture
    def application(self):
        return URLRouter(
            [
                re_path(r"^events/(?P<game_id>\w+)/$", GameEventsConsumer.as_asgi()),
            ]
        )

    @pytest.fixture
    def game(self):
        return GameFactory(master__user__username="master")

    @pytest.fixture
    def master_user(self):
        return User.objects.get(username="master")

    @pytest.fixture
    def player_user(self):
        return User.objects.get(character=CharacterFactory())

    @pytest.mark.asyncio
    async def test_message_from_master(self, application, game, master_user):
        communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
        communicator.scope["user"] = master_user
        communicator.scope["game_id"] = game.id
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
        assert EventSchema(**game_event)

        await communicator.send_json_to(game_event)
        response = await communicator.receive_json_from()
        assert response == game_event

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_message_from_player(self, application, game, player_user):
        communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
        communicator.scope["user"] = player_user
        communicator.scope["game_id"] = game.id
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
        assert EventSchema(**game_event)

        await communicator.send_json_to(game_event)
        response = await communicator.receive_json_from()
        assert response == game_event

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_quest_update(self, application, game, master_user):
        communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
        communicator.scope["user"] = master_user
        communicator.scope["game_id"] = game.id
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
        assert EventSchema(**game_event)

        await communicator.send_json_to(game_event)
        response = await communicator.receive_json_from()
        assert response == game_event

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_game_start(self, application, game, master_user):
        communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
        communicator.scope["user"] = master_user
        communicator.scope["game_id"] = game.id
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
        assert EventSchema(**game_event)

        await communicator.send_json_to(game_event)
        response = await communicator.receive_json_from()
        assert response == game_event

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_ability_check_request(self, application, game, master_user):
        communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
        communicator.scope["user"] = master_user
        communicator.scope["game_id"] = game.id
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
        assert EventSchema(**game_event)

        await communicator.send_json_to(game_event)
        response = await communicator.receive_json_from()
        assert response == game_event

        await communicator.disconnect()
