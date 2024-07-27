from .models.events import Event, QuestUpdate


def get_message(event: Event) -> str:
    message = ""
    if isinstance(event, QuestUpdate):
        message = "The Master created the campaign."
    return message
