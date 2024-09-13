def compute_ability_modifier(ability_score: int) -> int:
    """
    Compute ability modifier.

    The bigger ability score is, the bigger the modifier is, and vice versa.
    The formula is given by DnD rules.

    Args:
        ability_score (int): Ability score.

    Returns:
        int: The modifier corresponding to the score given as parameter.
    """

    return (ability_score - 10) // 2
