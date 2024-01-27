from enum import StrEnum

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class EventType(StrEnum):
    """Game event types.

    These event type are the types of messages that can be sent in the game chat.

    """

    MASTER_INSTRUCTION = "master.instruction"
    MASTER_START = "master.start"
    MASTER_QUEST = "master.quest"
    MASTER_ABILITY_CHECK = "master.ability.check"
    PLAYER_CHOICE = "player.choice"
    PLAYER_DICE_LAUNCH = "player.dice.launch"


def send_to_chat(game_id: int, event_type: str, content: str) -> None:
    """Send game events to the game chat.

    Send game events to the game channel layer.

    Args:
        game_id (int): Game identifier.
        event_type (str): Type of game event.
        content (str): Content of the event displayed on the chat.

    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"game_{game_id}_events",
        {"type": event_type, "content": content},
    )
