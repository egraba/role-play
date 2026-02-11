from __future__ import annotations

from typing import Any

from .constants.event_registry import get_event_type
from .constants.log_categories import LogCategory, get_category_for_event
from .models.events import DiceRoll, Event, RollResult, SpellCast
from .presenters import format_event_message


def serialize_game_log_event(event: Event) -> dict[str, Any]:
    """Serialize a game event for the game log panel."""
    event_type = get_event_type(event)
    category = get_category_for_event(event_type)

    # Master messages become DM category
    if hasattr(event.author, "master") and category == LogCategory.CHAT:
        category = LogCategory.DM

    author_name = str(event.author)
    character_id = None
    character_name = None

    if hasattr(event.author, "player") and event.author.player.character:
        character_id = event.author.player.character.id
        character_name = event.author.player.character.name

    return {
        "id": event.id,
        "type": event_type.value,
        "category": category.value,
        "date": event.date.isoformat(),
        "message": format_event_message(event),
        "author_name": author_name,
        "character_id": character_id,
        "character_name": character_name,
        "details": _get_event_details(event),
    }


def _get_event_details(event: Event) -> dict[str, Any] | None:
    """Get expanded details for the event."""
    if isinstance(event, DiceRoll):
        return {
            "dice_notation": event.dice_notation,
            "individual_rolls": event.individual_rolls,
            "modifier": event.modifier,
            "total": event.total,
            "roll_purpose": event.roll_purpose,
        }
    if isinstance(event, RollResult):
        return {
            "score": event.score,
            "result": event.get_result_display(),
            "ability_type": event.request.ability_type,
            "difficulty_class": event.request.difficulty_class,
        }
    if isinstance(event, SpellCast):
        return {
            "spell_name": event.spell.name,
            "slot_level": event.slot_level,
            "targets": [t.name for t in event.targets.all()],
        }
    return None
