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
    COMBAT_STARTED = "combat.started"
    TURN_STARTED = "turn.started"
    TURN_ENDED = "turn.ended"
    ROUND_ENDED = "round.ended"
    COMBAT_ENDED = "combat.ended"
    ACTION_TAKEN = "action.taken"
    # Spell events
    SPELL_CAST = "spell.cast"
    SPELL_DAMAGE_DEALT = "spell.damage.dealt"
    SPELL_HEALING_RECEIVED = "spell.healing.received"
    SPELL_CONDITION_APPLIED = "spell.condition.applied"
    SPELL_SAVING_THROW = "spell.saving.throw"
    # HP events
    HP_DAMAGE = "hp.damage"
    HP_HEAL = "hp.heal"
    HP_TEMP = "hp.temp"
    HP_DEATH_SAVE = "hp.death.save"
    # Dice roll events
    DICE_ROLL = "dice.roll"
    # Concentration events
    CONCENTRATION_SAVE_REQUIRED = "concentration.save.required"
    CONCENTRATION_SAVE_RESULT = "concentration.save.result"
    CONCENTRATION_BROKEN = "concentration.broken"
    CONCENTRATION_STARTED = "concentration.started"


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
    username: str
    date: datetime
    message: Optional[str] = None
    origin: Optional[EventOrigin] = None
