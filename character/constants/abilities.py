from django.db.models import TextChoices


class AbilityName(TextChoices):
    STRENGTH = "STR", "Strength"
    DEXTERITY = "DEX", "Dexterity"
    CONSTITUTION = "CON", "Constitution"
    INTELLIGENCE = "INT", "Intelligence"
    WISDOM = "WIS", "Wisdom"
    CHARISMA = "CHA", "Charisma"
