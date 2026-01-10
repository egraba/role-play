from django.db.models import TextChoices


class ConditionName(TextChoices):
    BLINDED = "blinded", "Blinded"
    CHARMED = "charmed", "Charmed"
    DEAFENED = "deafened", "Deafened"
    EXHAUSTION = "exhaustion", "Exhaustion"
    FRIGHTENED = "frightened", "Frightened"
    GRAPPLED = "grappled", "Grappled"
    INCAPACITATED = "incapacitated", "Incapacitated"
    INVISIBLE = "invisible", "Invisible"
    PARALYZED = "paralyzed", "Paralyzed"
    PETRIFIED = "petrified", "Petrified"
    POISONED = "poisoned", "Poisoned"
    PRONE = "prone", "Prone"
    RESTRAINED = "restrained", "Restrained"
    STUNNED = "stunned", "Stunned"
    UNCONSCIOUS = "unconscious", "Unconscious"
