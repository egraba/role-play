def format_message(message: str, sender_name: str = "") -> str:
    if sender_name == "":
        sender_name = "the Master"
    return f"{sender_name} said: {message}"
