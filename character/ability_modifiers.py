def compute_ability_modifier(ability_score: int) -> int:
    """
    The bigger ability score is, the bigger the modifier is, and vice versa.
    The formula is given by DnD rules.
    """

    return (ability_score - 10) // 2
