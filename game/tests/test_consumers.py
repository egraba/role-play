import pytest
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.urls import re_path
from faker import Faker

from character.tests.factories import CharacterFactory
from game.consumers import GameEventsConsumer
from game.exceptions import EventSchemaValidationError
from game.schemas import EventOrigin, EventSchema, EventType

from .factories import GameFactory, PlayerFactory

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


@pytest.mark.asyncio
async def test_game_start_handler(application, game, master_user):
    """Test game_start event handler."""
    communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
    communicator.scope["user"] = master_user
    communicator.scope["game_id"] = game.id
    connected, _ = await communicator.connect()
    assert connected

    fake = Faker()
    game_event = {
        "type": EventType.GAME_START,
        "username": master_user.username,
        "date": fake.date_time().isoformat(),
        "message": "Game started",
        "origin": EventOrigin.SERVER_SIDE,
    }

    await communicator.send_json_to(game_event)
    response = await communicator.receive_json_from()
    assert response["type"] == EventType.GAME_START

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_quest_update_handler(application, game, master_user):
    """Test quest_update event handler."""
    communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
    communicator.scope["user"] = master_user
    communicator.scope["game_id"] = game.id
    connected, _ = await communicator.connect()
    assert connected

    fake = Faker()
    game_event = {
        "type": EventType.QUEST_UPDATE,
        "username": master_user.username,
        "date": fake.date_time().isoformat(),
        "message": "Quest updated",
        "origin": EventOrigin.SERVER_SIDE,
    }

    await communicator.send_json_to(game_event)
    response = await communicator.receive_json_from()
    assert response["type"] == EventType.QUEST_UPDATE

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_ability_check_request_handler(application, game, master_user):
    """Test ability_check_request event handler."""
    communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
    communicator.scope["user"] = master_user
    communicator.scope["game_id"] = game.id
    connected, _ = await communicator.connect()
    assert connected

    fake = Faker()
    game_event = {
        "type": EventType.ABILITY_CHECK_REQUEST,
        "username": master_user.username,
        "date": fake.date_time().isoformat(),
        "message": "Roll for dexterity",
        "origin": EventOrigin.SERVER_SIDE,
    }

    await communicator.send_json_to(game_event)
    response = await communicator.receive_json_from()
    assert response["type"] == EventType.ABILITY_CHECK_REQUEST

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_ability_check_result_handler(application, game, master_user):
    """Test ability_check_result event handler."""
    communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
    communicator.scope["user"] = master_user
    communicator.scope["game_id"] = game.id
    connected, _ = await communicator.connect()
    assert connected

    fake = Faker()
    game_event = {
        "type": EventType.ABILITY_CHECK_RESULT,
        "username": master_user.username,
        "date": fake.date_time().isoformat(),
        "message": "Result: Success",
        "origin": EventOrigin.SERVER_SIDE,
    }

    await communicator.send_json_to(game_event)
    response = await communicator.receive_json_from()
    assert response["type"] == EventType.ABILITY_CHECK_RESULT

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_saving_throw_request_handler(application, game, master_user):
    """Test saving_throw_request event handler."""
    communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
    communicator.scope["user"] = master_user
    communicator.scope["game_id"] = game.id
    connected, _ = await communicator.connect()
    assert connected

    fake = Faker()
    game_event = {
        "type": EventType.SAVING_THROW_REQUEST,
        "username": master_user.username,
        "date": fake.date_time().isoformat(),
        "message": "Roll saving throw",
        "origin": EventOrigin.SERVER_SIDE,
    }

    await communicator.send_json_to(game_event)
    response = await communicator.receive_json_from()
    assert response["type"] == EventType.SAVING_THROW_REQUEST

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_saving_throw_result_handler(application, game, master_user):
    """Test saving_throw_result event handler."""
    communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
    communicator.scope["user"] = master_user
    communicator.scope["game_id"] = game.id
    connected, _ = await communicator.connect()
    assert connected

    fake = Faker()
    game_event = {
        "type": EventType.SAVING_THROW_RESULT,
        "username": master_user.username,
        "date": fake.date_time().isoformat(),
        "message": "Result: Success",
        "origin": EventOrigin.SERVER_SIDE,
    }

    await communicator.send_json_to(game_event)
    response = await communicator.receive_json_from()
    assert response["type"] == EventType.SAVING_THROW_RESULT

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_combat_initialization_handler(application, game, master_user):
    """Test combat_initialization event handler."""
    communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
    communicator.scope["user"] = master_user
    communicator.scope["game_id"] = game.id
    connected, _ = await communicator.connect()
    assert connected

    fake = Faker()
    game_event = {
        "type": EventType.COMBAT_INITIALIZATION,
        "username": master_user.username,
        "date": fake.date_time().isoformat(),
        "message": "Combat started",
        "origin": EventOrigin.SERVER_SIDE,
    }

    await communicator.send_json_to(game_event)
    response = await communicator.receive_json_from()
    assert response["type"] == EventType.COMBAT_INITIALIZATION

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_combat_initiative_request_handler(application, game, master_user):
    """Test combat_initiative_request event handler."""
    communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
    communicator.scope["user"] = master_user
    communicator.scope["game_id"] = game.id
    connected, _ = await communicator.connect()
    assert connected

    fake = Faker()
    game_event = {
        "type": EventType.COMBAT_INITIATIVE_REQUEST,
        "username": master_user.username,
        "date": fake.date_time().isoformat(),
        "message": "Roll initiative",
        "origin": EventOrigin.SERVER_SIDE,
    }

    await communicator.send_json_to(game_event)
    response = await communicator.receive_json_from()
    assert response["type"] == EventType.COMBAT_INITIATIVE_REQUEST

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_combat_initiative_result_handler(application, game, master_user):
    """Test combat_initiative_result event handler."""
    communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
    communicator.scope["user"] = master_user
    communicator.scope["game_id"] = game.id
    connected, _ = await communicator.connect()
    assert connected

    fake = Faker()
    game_event = {
        "type": EventType.COMBAT_INITIATIVE_RESULT,
        "username": master_user.username,
        "date": fake.date_time().isoformat(),
        "message": "Initiative: 15",
        "origin": EventOrigin.SERVER_SIDE,
    }

    await communicator.send_json_to(game_event)
    response = await communicator.receive_json_from()
    assert response["type"] == EventType.COMBAT_INITIATIVE_RESULT

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_combat_initialization_complete_handler(application, game, master_user):
    """Test combat_initialization_complete event handler."""
    communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
    communicator.scope["user"] = master_user
    communicator.scope["game_id"] = game.id
    connected, _ = await communicator.connect()
    assert connected

    fake = Faker()
    game_event = {
        "type": EventType.COMBAT_INITIALIZATION_COMPLETE,
        "username": master_user.username,
        "date": fake.date_time().isoformat(),
        "message": "Combat ready",
        "origin": EventOrigin.SERVER_SIDE,
    }

    await communicator.send_json_to(game_event)
    response = await communicator.receive_json_from()
    assert response["type"] == EventType.COMBAT_INITIALIZATION_COMPLETE

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_disconnect_without_connection(application, player_user):
    """Test disconnect when no game_group_name is set."""
    communicator = WebsocketCommunicator(application, "/events/99999/")
    communicator.scope["user"] = player_user
    communicator.scope["game_id"] = 99999
    # Try to connect to non-existent game, which will fail
    connected, _ = await communicator.connect()
    assert not connected
    # Disconnect should not raise even without game_group_name
    await communicator.disconnect()
