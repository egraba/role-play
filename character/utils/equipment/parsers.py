def parse_ac_settings(settings: str) -> tuple[int, int, int]:
    array = settings.split()
    base_ac = int(array[0])
    dexterity_modifier = 0
    bonus = 0
    return base_ac, dexterity_modifier, bonus
