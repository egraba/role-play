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
    ATTACK = "attack"
    CAST_SPELL = "cast_spell"
    DASH = "dash"
    DISENGAGE = "disangage"
    DODGE = "dodge"
    HELP = "help"
    HIDE = "hide"
    READY = "ready"
    SEARCH = "search"
    USE_OBJECT = "use_object"
