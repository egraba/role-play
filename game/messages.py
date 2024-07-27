from .models.events import Event, Quest


def get_message(event: Event) -> str:
    message = ""
    if isinstance(event, Quest):
        message = "The Master created the campaign."
    return message
