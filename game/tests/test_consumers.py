import pytest
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.urls import re_path
from faker import Faker

from game.consumers import GameEventsConsumer
from game.schemas import EventSchema, EventType, PlayerType
from utils.factories import UserFactory

from .factories import GameFactory

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
    return GameFactory(master__user__username="master")


@pytest.fixture
def user():
    return UserFactory()


@pytest.mark.asyncio
async def test_game_events_communication(application, game, user):
    communicator = WebsocketCommunicator(application, f"/events/{game.id}/")
    communicator.scope["user"] = user
    communicator.scope["game_id"] = game.id
    connected, _ = await communicator.connect()
    assert connected

    fake = Faker()
    date = fake.date_time().isoformat()
    message = fake.text(100)
    game_event = {
        "type": EventType.MESSAGE,
        "player_type": PlayerType.MASTER,
        "date": date,
        "message": message,
    }
    assert EventSchema(**game_event)

    await communicator.send_json_to(game_event)
    response = await communicator.receive_json_from()
    assert EventSchema(**response)

    await communicator.disconnect()
