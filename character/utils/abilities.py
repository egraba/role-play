from django.db.models import IntegerChoices


class AbilityScore(IntegerChoices):
    SCORE_15 = 15, "15"
    SCORE_14 = 14, "14"
    SCORE_13 = 13, "13"
    SCORE_12 = 12, "12"
    SCORE_10 = 10, "10"
    SCORE_8 = 8, "8"


def compute_ability_modifier(ability_score: int) -> int:
    """Compute ability modifier.

    The bigger ability score is, the bigger the modifier is, and vice versa.
    The formula is given by DnD rules.

    Args:
        ability_score (int): Ability score.

    Returns:
        int: The modifier corresponding to the score given as parameter.

    """

    return (ability_score - 10) // 2
