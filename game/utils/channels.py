import datetime
from enum import Flag, StrEnum, auto

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from pydantic import BaseModel


class GameEventOrigin(Flag):
    """Game event origin.

    These events can be initiated from the client side (e.g. via a browser),
    or via the server (e.g. via a form).

    """

    CLIENT_SIDE = auto()
    SERVER_SIDE = auto()


class GameEventType(StrEnum):
    """Game event type.

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
    """Game event.

    Game events are all the communication events that occur during a game.

    """

    event_origin: GameEventOrigin
    event_type: GameEventType
    event_date: datetime
    event_message: str


def send_to_chat(
    game_id: int, event_type: str, date: datetime, event_message: str
) -> None:
    """Send game events to the game chat.

    Send game events to the game channel layer.

    Args:
        game_id (int): Game identifier.
        event_type (str): Type of the game event.
        date (datetime): Date of the game event.
        event_message (str): Message related to the event to be displayed on the chat.

    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group=f"game_{game_id}_events",
        message={
            "origin": GameEventOrigin.SERVER_SIDE,
            "type": event_type,
            "date": date.isoformat(),
            "event_message": event_message,
        },
    )
