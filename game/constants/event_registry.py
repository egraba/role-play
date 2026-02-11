from __future__ import annotations

from typing import TYPE_CHECKING

from ..schemas import EventType

if TYPE_CHECKING:
    from ..models.events import Event

# Lazy import to avoid circular imports at module level.
# The dict is built on first call to get_event_type().
_EVENT_CLASS_TO_TYPE: dict[type[Event], EventType] | None = None


def _build_registry() -> dict[type[Event], EventType]:
    from ..models.events import (
        ActionTaken,
        CombatEnded,
        CombatInitativeOrderSet,
        CombatInitialization,
        CombatInitiativeRequest,
        CombatInitiativeResponse,
        CombatInitiativeResult,
        CombatStarted,
        ConcentrationBroken,
        ConcentrationSaveRequired,
        ConcentrationSaveResult,
        ConcentrationStarted,
        DiceRoll,
        GameStart,
        Message,
        QuestUpdate,
        RoundEnded,
        SpellCast,
        SpellConditionApplied,
        SpellDamageDealt,
        SpellHealingReceived,
        SpellSavingThrow,
        TurnEnded,
        TurnStarted,
        UserInvitation,
    )

    return {
        GameStart: EventType.GAME_START,
        UserInvitation: EventType.MESSAGE,
        Message: EventType.MESSAGE,
        QuestUpdate: EventType.QUEST_UPDATE,
        CombatInitialization: EventType.COMBAT_INITIALIZATION,
        CombatInitiativeRequest: EventType.COMBAT_INITIATIVE_REQUEST,
        CombatInitiativeResponse: EventType.COMBAT_INITIATIVE_RESPONSE,
        CombatInitiativeResult: EventType.COMBAT_INITIATIVE_RESULT,
        CombatInitativeOrderSet: EventType.COMBAT_INITIALIZATION_COMPLETE,
        CombatStarted: EventType.COMBAT_STARTED,
        TurnStarted: EventType.TURN_STARTED,
        TurnEnded: EventType.TURN_ENDED,
        RoundEnded: EventType.ROUND_ENDED,
        CombatEnded: EventType.COMBAT_ENDED,
        ActionTaken: EventType.ACTION_TAKEN,
        SpellCast: EventType.SPELL_CAST,
        SpellDamageDealt: EventType.SPELL_DAMAGE_DEALT,
        SpellHealingReceived: EventType.SPELL_HEALING_RECEIVED,
        SpellConditionApplied: EventType.SPELL_CONDITION_APPLIED,
        SpellSavingThrow: EventType.SPELL_SAVING_THROW,
        DiceRoll: EventType.DICE_ROLL,
        ConcentrationSaveRequired: EventType.CONCENTRATION_SAVE_REQUIRED,
        ConcentrationSaveResult: EventType.CONCENTRATION_SAVE_RESULT,
        ConcentrationBroken: EventType.CONCENTRATION_BROKEN,
        ConcentrationStarted: EventType.CONCENTRATION_STARTED,
    }


def _get_roll_event_type(event: Event) -> EventType:
    """Resolve event type for Roll* classes that depend on roll_type."""
    from ..constants.events import RollType
    from ..models.events import RollRequest, RollResponse, RollResult

    if isinstance(event, RollRequest):
        roll_type = event.roll_type
    elif isinstance(event, (RollResponse, RollResult)):
        roll_type = event.request.roll_type
    else:
        raise ValueError(f"Not a roll event: {type(event).__name__}")

    type_map = {
        RollRequest: {
            RollType.ABILITY_CHECK: EventType.ABILITY_CHECK_REQUEST,
            RollType.SAVING_THROW: EventType.SAVING_THROW_REQUEST,
        },
        RollResponse: {
            RollType.ABILITY_CHECK: EventType.ABILITY_CHECK_RESPONSE,
            RollType.SAVING_THROW: EventType.SAVING_THROW_RESPONSE,
        },
        RollResult: {
            RollType.ABILITY_CHECK: EventType.ABILITY_CHECK_RESULT,
            RollType.SAVING_THROW: EventType.SAVING_THROW_RESULT,
        },
    }

    event_class = type(event)
    if event_class not in type_map:
        raise ValueError(f"Not a roll event: {event_class.__name__}")

    inner = type_map[event_class]
    for key, value in inner.items():
        if key == roll_type:
            return value

    raise ValueError(f"Unsupported roll_type: {roll_type}")


def get_event_type(event: Event) -> EventType:
    """Look up the EventType for an event instance."""
    from ..models.events import RollRequest, RollResponse, RollResult

    if isinstance(event, (RollRequest, RollResponse, RollResult)):
        return _get_roll_event_type(event)

    global _EVENT_CLASS_TO_TYPE  # noqa: PLW0603
    if _EVENT_CLASS_TO_TYPE is None:
        _EVENT_CLASS_TO_TYPE = _build_registry()

    event_class = type(event)
    if event_class not in _EVENT_CLASS_TO_TYPE:
        raise NotImplementedError(
            f"{event_class.__name__} must be registered in event_registry"
        )

    return _EVENT_CLASS_TO_TYPE[event_class]
