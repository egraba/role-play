from typing import Any

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from pydantic import ValidationError

from ..schemas import GameEvent, GameEventError, GameEventOrigin


def send_to_channel(game_id: int, game_event: dict[str, Any]) -> None:
    """
    Send game events to the game channel layer.

    Args:
        game_id (int): Game identifier.
        game_event (dict[str, Any]): Game event.
    """
    # All the events sent by this function are server-side events.
    game_event["origin"] = GameEventOrigin.SERVER_SIDE
    try:
        GameEvent(**game_event)
    except ValidationError as exc:
        raise GameEventError(exc.errors()) from exc
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group=f"game_{game_id}_events", message=game_event
    )
