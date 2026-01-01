import pytest
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.urls import re_path
from faker import Faker

from character.tests.factories import CharacterFactory
from game.consumers import GameEventsConsumer
from game.exceptions import EventSchemaValidationError
from game.schemas import EventOrigin, EventSchema, EventType

from .factories import GameFactory, PlayerFactory, RollRequestFactory

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def application():
    return URLRouter(
        [
            re_path(r"^events/(?P<game_id>\w+)/$", GameEventsConsumer.as_asgi()),
        ]
    )


@pytest.fixture
def game():
    return GameFactory()


@pytest.fixture
def player_user(game):
    character = CharacterFactory()
    player = PlayerFactory(game=game, character=character)
    return player.user


@pytest.fixture
def master_user(game):
    return game.master.user


@pytest.mark.asyncio
async def test_connect_ok(application, game, player_user):
    communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
    communicator.scope["user"] = player_user
    communicator.scope["game_id"] = game.id
    connected, _ = await communicator.connect()
    assert connected


@pytest.mark.asyncio
async def test_connect_game_not_found(application, player_user):
    fake = Faker()
    game_id = fake.random_int(min=9999)
    communicator = WebsocketCommunicator(application, f"/events/{game_id}/")
    communicator.scope["user"] = player_user
    communicator.scope["game_id"] = game_id
    connected, _ = await communicator.connect()
    assert not connected


@pytest.mark.asyncio
async def test_communication_schema_not_valid(application, game, player_user):
    communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
    communicator.scope["user"] = player_user
    communicator.scope["game_id"] = game.id
    connected, _ = await communicator.connect()
    assert connected

    game_event = {
        "some_field": "some_value",
    }

    await communicator.send_json_to(game_event)
    with pytest.raises(EventSchemaValidationError):
        await communicator.receive_json_from()
        await communicator.disconnect()


@pytest.mark.asyncio
async def test_communication_message_from_master(application, game, master_user):
    communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
    communicator.scope["user"] = master_user
    communicator.scope["game_id"] = game.id
    connected, _ = await communicator.connect()
    assert connected

    fake = Faker()
    date = fake.date_time().isoformat()
    message = fake.text(100)
    game_event = {
        "type": EventType.MESSAGE,
        "username": master_user.username,
        "date": date,
        "message": message,
    }

    await communicator.send_json_to(game_event)
    response = await communicator.receive_json_from()
    assert EventSchema(**response)

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_communication_message_from_player(application, game, player_user):
    communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
    communicator.scope["user"] = player_user
    communicator.scope["game_id"] = game.id
    connected, _ = await communicator.connect()
    assert connected

    fake = Faker()
    date = fake.date_time().isoformat()
    message = fake.text(100)
    game_event = {
        "type": EventType.MESSAGE,
        "username": player_user.username,
        "date": date,
        "message": message,
    }

    await communicator.send_json_to(game_event)
    response = await communicator.receive_json_from()
    assert EventSchema(**response)

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_communication_server_side_event(application, game, master_user):
    """Test that server-side events are passed through without storing."""
    communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
    communicator.scope["user"] = master_user
    communicator.scope["game_id"] = game.id
    connected, _ = await communicator.connect()
    assert connected

    fake = Faker()
    date = fake.date_time().isoformat()
    message = fake.text(100)
    game_event = {
        "type": EventType.MESSAGE,
        "username": master_user.username,
        "date": date,
        "message": message,
        "origin": EventOrigin.SERVER_SIDE,
    }

    await communicator.send_json_to(game_event)
    response = await communicator.receive_json_from()
    assert EventSchema(**response)

    await communicator.disconnect()
