from django.db.models import TextChoices


COMBAT_CHOICES = {"is_fighting": "Is fighting?", "is_suprised": "Is surprised?"}


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
