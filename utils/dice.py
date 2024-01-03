import re

DICE_REGEX = "(\d+)?d(\d+)([\+\-]\d+)?"

dice_types = {4, 6, 8, 10, 12, 20}
"""set[int]: Dice types.

The dice type is the number of dice faces.

"""


class DiceStringFormatError(TypeError):
    """Raised when a dice string is wrongly formatted."""

    pass


class Dice(str):
    def __init__(self, dice_str):
        super().__init__()
        if not re.match(DICE_REGEX, self):
            raise DiceStringFormatError(f"[{self}] does not match a dice regex...")
        dice_str_parts = self.split("d")
        self.throws = int(dice_str_parts[0])
        dice_type = int(dice_str_parts[1])
        if dice_type not in dice_types:
            raise DiceStringFormatError("The provided dice type is not supported...")
        self.type = dice_type

    def add_throws(self, throws):
        """Add throws to a dice string.

        A dice string looks like 'NdT', where N is the number of throws
        and T the type of the dice.
        This method adds the throws passed as parameter to N.

        Args:
            dice_str (str): Dice string.

        """

        self.throws += throws
        self = f"{self.throws}d{self.type}"
        return self
