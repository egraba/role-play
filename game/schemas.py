from datetime import datetime
from enum import IntFlag, StrEnum, auto
from typing import Optional

from pydantic import BaseModel


class GameEventType(StrEnum):
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
    COMBAT_INITIATION = "combat.initiation"
    COMBAT_ROLL_INITIATIVE = "combat.roll.initiative"


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
