from django.db.models import IntegerChoices


class AbilityScore(IntegerChoices):
    SCORE_15 = 15, "15"
    SCORE_14 = 14, "14"
    SCORE_13 = 13, "13"
    SCORE_12 = 12, "12"
    SCORE_10 = 10, "10"
    SCORE_8 = 8, "8"


def compute_ability_modifier(ability_score):
    return (ability_score - 10) // 2
