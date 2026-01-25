import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from pydantic import ValidationError

from ..exceptions import EventSchemaValidationError
from ..models.events import Event
from ..schemas import (
    EventOrigin,
    EventSchema,
    EventType,
)


def _get_event_type(event: Event) -> EventType:
    """
    Retrieve event type according to Event instance class.

    Delegates to the event's get_event_type() method.
    """
    return event.get_event_type()


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
