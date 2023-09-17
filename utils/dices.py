import re

DICE_REGEX = "(\d+)?d(\d+)([\+\-]\d+)?"

types = (4, 6, 8, 10, 12, 20)


class DiceError(Exception):
    pass


class Dice:
    def __init__(self, dice_str):
        if not re.match(DICE_REGEX, dice_str):
            raise TypeError(f"[{dice_str}] does not match a dice regex...")
        dice_elems = dice_str.split("d")
        self.throws = int(dice_elems[0])
        dice_type = int(dice_elems[1])
        if dice_type not in types:
            raise DiceError("The provided dice type is not supported...")
        self.type = dice_type

    def __str__(self):
        return f"{self.throws}d{self.type}"
