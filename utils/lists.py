def item_in_choices(name, choices) -> bool:
    return bool([item for item in choices if name in item])
