from datetime import datetime
from enum import IntFlag, StrEnum, auto
from typing import Optional

from pydantic import BaseModel


class EventType(StrEnum):
    """
    The game event type corresponds to a specific action that can be done during a game.
    """

    MESSAGE = "message"
    GAME_START = "game.start"
    QUEST_UPDATE = "quest.update"
    ABILITY_CHECK_REQUEST = "ability.check.request"
    ABILITY_CHECK = "ability.check"
    ABILITY_CHECK_RESULT = "ability.check.result"
    SAVING_THROW_REQUEST = "saving.throw.request"
    SAVING_THROW = "saving.throw"
    SAVING_THROW_RESULT = "saving.throw.result"
    COMBAT_INITIALIZATION = "combat.initialization"
    COMBAT_ROLL_INITIATIVE = "combat.roll.initiative"


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
    username: Optional[str] = None
    message: str
    origin: Optional[EventOrigin] = None


class EventSchemaValidationError(TypeError):
    pass
