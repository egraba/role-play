import pytest
from django.utils import timezone

from game.schemas import GameEventError, GameEventOrigin, GameEventType, PlayerType
from game.utils.channels import send_to_channel

from ..factories import GameFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def game():
    return GameFactory()


def test_send_to_channel_origin_is_server(game):
    game_event = {
        "type": GameEventType.GAME_START,
        "player_type": PlayerType.MASTER,
        "date": timezone.now().isoformat(),
        "message": "tamer",
    }
    send_to_channel(game.id, game_event)
    assert game_event["origin"] == GameEventOrigin.SERVER_SIDE


def test_send_to_channel_invalid_game_event(game):
    game_event = {
        "type": GameEventType.GAME_START,
        "date": timezone.now().isoformat(),
        "message": "tamer",
    }
    with pytest.raises(GameEventError):
        send_to_channel(game.id, game_event)
