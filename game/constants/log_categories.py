from enum import StrEnum

from ..schemas import EventType


class LogCategory(StrEnum):
    """Categories for game log entries."""

    ROLLS = "rolls"
    COMBAT = "combat"
    SPELLS = "spells"
    CHAT = "chat"
    DM = "dm"


# Map event types to log categories
EVENT_TYPE_TO_CATEGORY: dict[EventType, LogCategory] = {
    # Rolls
    EventType.DICE_ROLL: LogCategory.ROLLS,
    EventType.ABILITY_CHECK_RESULT: LogCategory.ROLLS,
    EventType.SAVING_THROW_RESULT: LogCategory.ROLLS,
    EventType.COMBAT_INITIATIVE_RESULT: LogCategory.ROLLS,
    # Combat
    EventType.COMBAT_INITIALIZATION: LogCategory.COMBAT,
    EventType.COMBAT_INITIALIZATION_COMPLETE: LogCategory.COMBAT,
    EventType.COMBAT_STARTED: LogCategory.COMBAT,
    EventType.TURN_STARTED: LogCategory.COMBAT,
    EventType.TURN_ENDED: LogCategory.COMBAT,
    EventType.ROUND_ENDED: LogCategory.COMBAT,
    EventType.COMBAT_ENDED: LogCategory.COMBAT,
    EventType.ACTION_TAKEN: LogCategory.COMBAT,
    EventType.HP_DAMAGE: LogCategory.COMBAT,
    EventType.HP_HEAL: LogCategory.COMBAT,
    EventType.HP_TEMP: LogCategory.COMBAT,
    EventType.HP_DEATH_SAVE: LogCategory.COMBAT,
    # Spells
    EventType.SPELL_CAST: LogCategory.SPELLS,
    EventType.SPELL_DAMAGE_DEALT: LogCategory.SPELLS,
    EventType.SPELL_HEALING_RECEIVED: LogCategory.SPELLS,
    EventType.SPELL_CONDITION_APPLIED: LogCategory.SPELLS,
    EventType.SPELL_SAVING_THROW: LogCategory.SPELLS,
    EventType.CONCENTRATION_SAVE_REQUIRED: LogCategory.SPELLS,
    EventType.CONCENTRATION_SAVE_RESULT: LogCategory.SPELLS,
    EventType.CONCENTRATION_BROKEN: LogCategory.SPELLS,
    EventType.CONCENTRATION_STARTED: LogCategory.SPELLS,
    # Chat/DM determined by author, default to chat
    EventType.MESSAGE: LogCategory.CHAT,
    EventType.QUEST_UPDATE: LogCategory.DM,
    EventType.GAME_START: LogCategory.DM,
}


def get_category_for_event(event_type: EventType) -> LogCategory:
    """Get the log category for an event type."""
    return EVENT_TYPE_TO_CATEGORY.get(event_type, LogCategory.CHAT)
