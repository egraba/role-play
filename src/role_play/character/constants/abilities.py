from django.db.models import IntegerChoices, TextChoices


class AbilityName(TextChoices):
    STRENGTH = "STR", "Strength"
    DEXTERITY = "DEX", "Dexterity"
    CONSTITUTION = "CON", "Constitution"
    INTELLIGENCE = "INT", "Intelligence"
    WISDOM = "WIS", "Wisdom"
    CHARISMA = "CHA", "Charisma"


class AbilityScore(IntegerChoices):
    SCORE_15 = 15, "15"
    SCORE_14 = 14, "14"
    SCORE_13 = 13, "13"
    SCORE_12 = 12, "12"
    SCORE_10 = 10, "10"
    SCORE_8 = 8, "8"
