import datetime
from typing import Any

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from pydantic import ValidationError

from ..constants.log_categories import LogCategory, get_category_for_event
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


def _get_category(event: Event) -> str:
    """Get the log category for an event, considering author type."""
    event_type = event.get_event_type()
    category = get_category_for_event(event_type)

    # Master messages become DM category
    if hasattr(event.author, "master") and category == LogCategory.CHAT:
        return LogCategory.DM.value

    return category.value


def build_event_payload(event: Event) -> dict[str, Any]:
    """Build the complete event payload for WebSocket broadcast."""
    if isinstance(event.date, int):
        event.date = datetime.datetime.fromtimestamp(event.date / 1e3)

    payload = {
        "type": _get_event_type(event),
        "username": event.author.user.username,
        "date": event.date.isoformat(),
        "message": event.get_message(),
        "origin": EventOrigin.SERVER_SIDE,
        "category": _get_category(event),
        "character_id": None,
        "character_name": None,
    }

    # Add character info for player events
    if hasattr(event.author, "player") and event.author.player.character:
        payload["character_id"] = event.author.player.character.id
        payload["character_name"] = event.author.player.character.name

    return payload


def send_to_channel(event: Event) -> None:
    """
    Serialize a game event to JSON and send it in the right channel.
    """
    game_event = build_event_payload(event)

    try:
        EventSchema(
            type=game_event["type"],
            username=game_event["username"],
            date=event.date,
            message=game_event["message"],
            origin=game_event["origin"],
        )
    except ValidationError as exc:
        raise EventSchemaValidationError(exc.errors()) from exc

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group=f"game_{event.game.id}_events", message=game_event
    )
