scores = [(15, 15), (14, 14), (13, 13), (12, 12), (10, 10), (8, 8)]


def compute_ability_modifier(ability_score):
    return (ability_score - 10) // 2
