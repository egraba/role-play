ABILITY_TYPES_KEY = "ability_types"  # type: str
"""Ability type cache key."""


def advancement_key(level: int) -> str:
    """Advancement cache key."""
    return f"advancement_{level}"


def character_key(character_id: int) -> str:
    """Character cache key."""
    return f"character_{character_id}"
