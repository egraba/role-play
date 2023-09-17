import re


def add_throws(dice, throws):
    if not re.match("(\d+)?d(\d+)([\+\-]\d+)?", dice):
        raise TypeError(f"[{dice}] does not match a dice regex...")
    dice_elems = dice.split("d")
    throw_elem = int(dice_elems[0])
    throw_elem += throws
    dice = f"{throw_elem}d{dice_elems[1]}"
    return dice
