from django.db.models import TextChoices


class FeatType(TextChoices):
    ORIGIN = "O", "Origin"
    GENERAL = "G", "General"


class FeatName(TextChoices):
    ALERT = "alert", "Alert"
    MAGIC_INITIATE_CLERIC = "magic_initiate_cleric", "Magic Initiate (Cleric)"
    MAGIC_INITIATE_WIZARD = "magic_initiate_wizard", "Magic Initiate (Wizard)"
    SAVAGE_ATTACKER = "savage_attacker", "Savage Attacker"
