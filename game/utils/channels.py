from datetime import datetime
from enum import IntFlag, StrEnum, auto
from typing import Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from pydantic import BaseModel, ValidationError


class GameEventOrigin(IntFlag):
    """
    Game event origin.

    These events can be initiated from the client side (e.g. via a browser),
    or via the server (e.g. via a form).

    """

    CLIENT_SIDE = auto()
    SERVER_SIDE = auto()


class GameEventType(StrEnum):
    """
    Game event type.

    The type corresponds to a specific action that can be done during a game.

    The events prefixed by "MASTER" are done by the Dungeon Master (DM), while
    the events prefixed by "PLAYER" are done by the players.

    """

    MASTER_INSTRUCTION = "master.instruction"
    MASTER_GAME_START = "master.game.start"
    MASTER_QUEST_UPDATE = "master.quest.update"
    MASTER_ABILITY_CHECK_REQUEST = "master.ability.check.request"
    PLAYER_CHOICE = "player.choice"
    PLAYER_DICE_LAUNCH = "player.dice.launch"


class GameEvent(BaseModel):
    """
    Game event.

    Game events are all the communication events that occur during a game.

    """

    type: GameEventType  # "type" field is necessary for Django channels.
    event_date: datetime
    event_message: str
    event_origin: Optional[GameEventOrigin] = None


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
    game_event["event_origin"] = GameEventOrigin.SERVER_SIDE
    try:
        GameEvent(**game_event)
    except ValidationError as e:
        raise GameEventError(e.errors())

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group=f"game_{game_id}_events", message=game_event
    )
