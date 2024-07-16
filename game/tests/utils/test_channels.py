import pytest
from django.utils import timezone

from game.schemas import EventOrigin, EventType, PlayerType
from game.utils.channels import send_to_channel

from ..factories import GameFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def game():
    return GameFactory()


def test_send_to_channel_origin_is_server(game):
    game_event = {
        "type": EventType.GAME_START,
        "player_type": PlayerType.MASTER,
        "date": timezone.now().isoformat(),
        "message": "tamer",
    }
    send_to_channel(game.id, game_event)
    assert game_event["origin"] == EventOrigin.SERVER_SIDE
