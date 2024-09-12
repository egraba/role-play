import re
from collections import UserString

import dice

DICE_REGEX = r"(\d+)?d(\d+)([\+\-]\d+)?"

dice_types = {4, 6, 8, 10, 12, 20}
"""The dice type is the number of dice faces."""


class DiceStringFormatError(Exception):
    """Raised when a dice string is wrongly formatted."""


class Dice(UserString):
    """
    Class managing dice strings.

    A dice string looks like '[N]dT', where N is the number of dice throws
        and T the type of the dice.

    Attributes:
        throws (int): Number of throws.
        type (int): Dice type.
    """

    def __init__(self, dice_str: str):
        super().__init__(dice_str)
        if not re.match(DICE_REGEX, dice_str):
            raise DiceStringFormatError(f"[{dice_str}] does not match a dice regex...")
        dice_str_parts = self.split("d")
        try:
            self.throws = int(dice_str_parts[0])
        except ValueError:
            # This is raised when no throw is specified in the dice string.
            self.throws = 1
        dice_type = int(dice_str_parts[1])
        if dice_type not in dice_types:
            raise DiceStringFormatError("The provided dice type is not supported...")
        self.type = dice_type

    def add_throws(self, throws: int) -> str:
        """
        Add throws to a dice string.

        Args:
            throws (int): Number of throws.

        Returns:
            str: New dice string.
        """

        if throws <= 0:
            raise DiceStringFormatError(
                "The number of throws must be a strictly positive integer..."
            )
        if self.throws is None:
            self.throws = 0
        self.throws += throws
        self.data = f"{self.throws}d{self.type}"
        return self.data

    def roll(self, modifier: int = 0) -> int:
        """
        Rolls the dice.

        In case of several rolls, it sums the values of each roll and adds
        the modifier value (if any).

        Args:
            modifier (int): Positive or negative integer to add on a roll.

        Returns:
            int: Sum of dice rolls results.
        """
        return sum(list(dice.roll(self.data))) + modifier
