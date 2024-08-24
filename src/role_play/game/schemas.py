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
    ABILITY_CHECK_RESPONSE = "ability.check.response"
    ABILITY_CHECK_RESULT = "ability.check.result"
    SAVING_THROW_REQUEST = "saving.throw.request"
    SAVING_THROW_RESPONSE = "saving.throw.response"
    SAVING_THROW_RESULT = "saving.throw.result"
    COMBAT_INITIALIZATION = "combat.initialization"
    COMBAT_INITIATIVE_REQUEST = "combat.initiative.request"
    COMBAT_INITIATIVE_RESPONSE = "combat.initiative.response"
    COMBAT_INITIATIVE_RESULT = "combat.initiative.result"
    COMBAT_INITIALIZATION_COMPLETE = "combat.initialization.complete"


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
    message: Optional[str] = None
    origin: Optional[EventOrigin] = None
