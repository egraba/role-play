import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from pydantic import ValidationError

from ..constants.events import RollType
from ..exceptions import EventSchemaValidationError
from ..models.events import (
    CombatInitialization,
    CombatInitiativeRequest,
    CombatInitiativeResponse,
    CombatInitiativeResult,
    Event,
    GameStart,
    QuestUpdate,
    RollRequest,
    RollResponse,
    RollResult,
)
from ..schemas import (
    EventOrigin,
    EventSchema,
    EventType,
    PlayerType,
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
        event_type = EventType.COMBAT_INITIATIVE_RESPONSE
    return event_type


def send_to_channel(event: Event) -> None:
    """
    Serialize an game event to a JSON and send it in the right channel.
    """
    if isinstance(event.date, int):
        event.date = datetime.datetime.fromtimestamp(event.date / 1e3)
    game_event = {
        "type": _get_event_type(event),
        "date": event.date.isoformat(),
        "player_type": PlayerType.MASTER,
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
