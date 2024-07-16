from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from ..models.events import Event
from ..schemas import EventSchema, EventOrigin, PlayerType


def send_to_channel(event: Event) -> None:
    """
    Serialize an game event to a JSON and send it in the right channel.
    """
    game_event = EventSchema(
        type=None,
        date=event.date,
        player_type=PlayerType.MASTER,
        message=event.message,
        origin=EventOrigin.SERVER_SIDE,
    )
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group=f"game_{event.game.id}_events", message=game_event
    )
