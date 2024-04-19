def parse_ac_settings(settings: str) -> tuple[int, bool, int]:
    base_ac = 0
    is_dex_modifier = False
    bonus = 0
    array = settings.split()
    first_part = array[0]
    if first_part.startswith("+"):
        bonus = int(first_part)
    else:
        base_ac = int(array[0])
        second_part = " ".join(array[2:])
        if second_part.startswith("Dex modifier"):
            is_dex_modifier = True
    return base_ac, is_dex_modifier, bonus
