from django.db.models import TextChoices


class CombatState(TextChoices):
    """State of a combat encounter."""

    ROLLING_INITIATIVE = "RI", "Rolling Initiative"
    ACTIVE = "A", "Active"
    ENDED = "E", "Ended"


class FighterAttributeChoices(TextChoices):
    IS_FIGHTING = "is_fighting", "Is fighting?"
    IS_SURPRISED = "is_suprised", "Is surprised?"


class CombatAction(TextChoices):
    ATTACK = "attack", "Attack"
    CAST_SPELL = "cast_spell", "Cast a Spell"
    DASH = "dash", "Dash"
    DISENGAGE = "disengage", "Disengage"
    DODGE = "dodge", "Dodge"
    HELP = "help", "Help"
    HIDE = "hide", "Hide"
    READY = "ready", "Ready"
    SEARCH = "search", "Search"
    USE_OBJECT = "use_object", "Use an Object"


class ActionType(TextChoices):
    """Type of action in the action economy."""

    ACTION = "A", "Action"
    BONUS_ACTION = "B", "Bonus Action"
    REACTION = "R", "Reaction"
