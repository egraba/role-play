from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from ..constants.events import RollType
from ..models.combat import Combat
from ..models.events import Event, GameStart, Quest, RollRequest
from ..schemas import EventOrigin, EventSchema, EventType, PlayerType


def _get_event_type(event: Event) -> EventType:
    """
    Retrieve event type according to Event instance class.
    """
    if isinstance(event, Quest):
        event_type = EventType.QUEST_UPDATE
    elif isinstance(event, GameStart):
        event_type = EventType.GAME_START
    elif isinstance(event, RollRequest):
        if event.roll_type == RollType.ABILITY_CHECK:
            event_type = EventType.ABILITY_CHECK_REQUEST
    elif isinstance(event, Combat):
        event_type = EventType.COMBAT_INITIATION
    return event_type


def send_to_channel(event: Event) -> None:
    """
    Serialize an game event to a JSON and send it in the right channel.
    """
    game_event = EventSchema(
        type=_get_event_type(event),
        date=event.date,
        player_type=PlayerType.MASTER,
        message=event.message,
        origin=EventOrigin.SERVER_SIDE,
    )
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group=f"game_{event.game.id}_events", message=game_event
    )
