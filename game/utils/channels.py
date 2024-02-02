from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from pydantic import ValidationError

from ..schemas import GameEvent, GameEventError, GameEventOrigin


def send_to_channel(game_id: int, game_event: dict[GameEvent]) -> None:
    """
    Send game events to the game channel layer.

    Args:
        game_id (int): Game identifier.
        game_event (dict[GameEvent]): Game event.
    """
    # All the events sent by this function are server-side events.
    game_event["origin"] = GameEventOrigin.SERVER_SIDE
    try:
        GameEvent(**game_event)
    except ValidationError as e:
        raise GameEventError(e.errors())

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group=f"game_{game_id}_events", message=game_event
    )
