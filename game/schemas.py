from datetime import datetime
from enum import IntFlag, StrEnum, auto
from typing import Optional

from pydantic import BaseModel

from .constants.events import EventType


class PlayerType(StrEnum):
    """Type of player in a game."""

    MASTER = "master"
    PLAYER = "player"


class EventOrigin(IntFlag):
    """
    Game events can be initiated from the client side (e.g. via a browser),
    or via the server (e.g. via a form).
    """

    CLIENT_SIDE = auto()
    SERVER_SIDE = auto()


class EventSchema(BaseModel):
    """Schema used for communication within channels."""

    type: EventType  # "type" field is necessary for Django channels.
    date: datetime
    player_type: PlayerType
    message: str
    origin: Optional[EventOrigin] = None
