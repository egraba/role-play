import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from pydantic import ValidationError

from ..constants.events import RollType
from ..exceptions import EventSchemaValidationError
from ..models.events import (
    ActionTaken,
    CombatEnded,
    CombatInitativeOrderSet,
    CombatInitialization,
    CombatInitiativeRequest,
    CombatInitiativeResponse,
    CombatInitiativeResult,
    CombatStarted,
    Event,
    GameStart,
    QuestUpdate,
    RollRequest,
    RollResponse,
    RollResult,
    RoundEnded,
    TurnEnded,
    TurnStarted,
)
from ..schemas import (
    EventOrigin,
    EventSchema,
    EventType,
)


def _get_event_type(event: Event) -> EventType:
    """
    Retrieve event type according to Event instance class.
    """
    if isinstance(event, QuestUpdate):
        event_type = EventType.QUEST_UPDATE
    elif isinstance(event, GameStart):
        event_type = EventType.GAME_START
    elif isinstance(event, RollRequest):
        if event.roll_type == RollType.ABILITY_CHECK:
            event_type = EventType.ABILITY_CHECK_REQUEST
        elif event.roll_type == RollType.SAVING_THROW:
            event_type = EventType.SAVING_THROW_REQUEST
    elif isinstance(event, RollResponse):
        if event.request.roll_type == RollType.ABILITY_CHECK:
            event_type = EventType.ABILITY_CHECK_RESPONSE
    elif isinstance(event, RollResult):
        if event.request.roll_type == RollType.ABILITY_CHECK:
            event_type = EventType.ABILITY_CHECK_RESULT
        if event.request.roll_type == RollType.SAVING_THROW:
            event_type = EventType.SAVING_THROW_RESULT
    elif isinstance(event, CombatInitialization):
        event_type = EventType.COMBAT_INITIALIZATION
    elif isinstance(event, CombatInitiativeRequest):
        event_type = EventType.COMBAT_INITIATIVE_REQUEST
    elif isinstance(event, CombatInitiativeResponse):
        event_type = EventType.COMBAT_INITIATIVE_RESPONSE
    elif isinstance(event, CombatInitiativeResult):
        event_type = EventType.COMBAT_INITIATIVE_RESULT
    elif isinstance(event, CombatInitativeOrderSet):
        event_type = EventType.COMBAT_INITIALIZATION_COMPLETE
    elif isinstance(event, CombatStarted):
        event_type = EventType.COMBAT_STARTED
    elif isinstance(event, TurnStarted):
        event_type = EventType.TURN_STARTED
    elif isinstance(event, TurnEnded):
        event_type = EventType.TURN_ENDED
    elif isinstance(event, RoundEnded):
        event_type = EventType.ROUND_ENDED
    elif isinstance(event, CombatEnded):
        event_type = EventType.COMBAT_ENDED
    elif isinstance(event, ActionTaken):
        event_type = EventType.ACTION_TAKEN
    return event_type


def send_to_channel(event: Event) -> None:
    """
    Serialize an game event to a JSON and send it in the right channel.
    """
    if isinstance(event.date, int):
        event.date = datetime.datetime.fromtimestamp(event.date / 1e3)
    game_event = {
        "type": _get_event_type(event),
        "username": event.author.user.username,
        "date": event.date.isoformat(),
        "message": event.get_message(),
        "origin": EventOrigin.SERVER_SIDE,
    }
    try:
        EventSchema(**game_event)
    except ValidationError as exc:
        raise EventSchemaValidationError(exc.errors()) from exc
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group=f"game_{event.game.id}_events", message=game_event
    )
