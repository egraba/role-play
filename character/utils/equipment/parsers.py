def parse_ac_settings(settings: str) -> tuple[int, bool, int, int]:
    """
    Parse Armor Class (AC) settings.
    These settings have the following form:
        N + Dex modifier [(max 2)]
        or
        +N
    where N is an integer.
    The +N format means that N has to be added to character's AC.
    """
    base_ac = 0
    is_dex_modifier = False
    modifier_max = 0
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
            if second_part.endswith("(max 2)"):
                modifier_max = 2
    return base_ac, is_dex_modifier, modifier_max, bonus


def parse_strength(settings: str) -> int:
    """
    Parse stealth settings.
    These settings have the following form:
        Str N
    where N is an integer.
    """
    max_strength = 0
    if settings == "" or settings is None:
        return max_strength
    array = settings.split()
    if array[0] == "Str":
        max_strength = int(array[1])
    return max_strength
