import re

DICE_REGEX = "(\d+)?d(\d+)([\+\-]\d+)?"

types = (4, 6, 8, 10, 12, 20)


class DiceFormatError(TypeError):
    """Raised when a dice string is wrongly formatted."""

    pass


def add_throws(dice_str, throws):
    """Add throws to a dice string.

    A dice string looks like 'NdT', where N is the number of throws
    and T the type of the dice.
    This function adds the throws passed as parameter to N.

    Args:
        dice_str (str): Dice string.
        throws (int): Number of throws to add to the dice string.

    Returns:
        str: New dice string with added throws.

    """

    if not re.match(DICE_REGEX, dice_str):
        raise DiceFormatError(f"[{dice_str}] does not match a dice regex...")
    dice_str_parts = dice_str.split("d")
    dice_type = int(dice_str_parts[1])
    if dice_type not in types:
        raise DiceFormatError("The provided dice type is not supported...")

    dice_str_parts[0] = str(int(dice_str_parts[0]) + throws)
    dice_str = "d".join(dice_str_parts)
    return dice_str
