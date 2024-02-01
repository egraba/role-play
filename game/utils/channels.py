from datetime import datetime
from enum import IntFlag, StrEnum, auto
from typing import Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from pydantic import BaseModel, ValidationError


class GameEventType(StrEnum):
    """
    The game event type corresponds to a specific action that can be done during a game.
    """

    MESSAGE = "message"
    GAME_START = "game.start"
    QUEST_UPDATE = "quest.update"
    ABILITY_CHECK_REQUEST = "ability.check.request"
    DICE_LAUNCH = "dice.launch"


class PlayerType(StrEnum):
    """Type of player in a game."""

    MASTER = "master"
    PLAYER = "player"


class GameEventOrigin(IntFlag):
    """
    Game events can be initiated from the client side (e.g. via a browser),
    or via the server (e.g. via a form).
    """

    CLIENT_SIDE = auto()
    SERVER_SIDE = auto()


class GameEvent(BaseModel):
    """Game events are all the communication events that occur during a game."""

    type: GameEventType  # "type" field is necessary for Django channels.
    date: datetime
    player_type: PlayerType
    message: str
    origin: Optional[GameEventOrigin] = None


class GameEventError(TypeError):
    """Raised when an error occurs during GameEvent schema validation."""

    pass


def send_to_channel(game_id: int, game_event: dict[GameEvent]) -> None:
    """
    Send game events to the game channel layer.

    Args:
        game_id (int): Game identifier.
        game_event (dict[GameEvent]): Game event.
    """
    # All the events sent by this function are server-side events.
    game_event["origin"] = GameEventOrigin.SERVER_SIDE
    try:
        GameEvent(**game_event)
    except ValidationError as e:
        raise GameEventError(e.errors())

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group=f"game_{game_id}_events", message=game_event
    )
