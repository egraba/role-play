def parse_ac_settings(settings: str) -> tuple[int, int, int]:
    base_ac = 0
    dexterity_modifier = 0
    bonus = 0
    array = settings.split()
    first_part = array[0]
    if first_part.startswith("+"):
        bonus = int(first_part)
    else:
        base_ac = int(array[0])
    return base_ac, dexterity_modifier, bonus
