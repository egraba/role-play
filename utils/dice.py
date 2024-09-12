import re
from collections import UserString

import dice

DICE_REGEX = r"(\d+)?d(\d+)([\+\-]\d+)?"

dice_types = {4, 6, 8, 10, 12, 20}
"""The dice type is the number of dice faces."""


class DiceStringFormatError(Exception):
    """Raised when a dice string is wrongly formatted."""


class DiceString(UserString):
    """
    A dice string looks like '[N]dT', where N is the number of dice throws
    and T the type of the dice.

    Attributes:
        nb_throws (int): Number of throws.
        dice_type (int): Dice type.
    """

    def __init__(self, dice_str: str):
        super().__init__(dice_str)
        if not re.match(DICE_REGEX, dice_str):
            raise DiceStringFormatError(f"{dice_str=} is not a dice string")
        dice_str_parts = self.split("d")
        try:
            self.nb_throws = int(dice_str_parts[0])
        except ValueError:
            # This is raised when no throw is specified in the dice string.
            self.nb_throws = 1
        dice_type = int(dice_str_parts[1])
        if dice_type not in dice_types:
            raise DiceStringFormatError(f"{dice_type=} is not supported")
        self.type = dice_type

    def add_throws(self, nb_throws: int) -> str:
        """
        Add throws to a dice string.

        Args:
            nb_throws (int): Number of throws to add.

        Returns:
            str: The new dice string.
        """

        if nb_throws <= 0:
            raise DiceStringFormatError(
                f"{nb_throws=} must be a strictly positive integer"
            )
        if self.nb_throws is None:
            self.nb_throws = 0
        self.nb_throws += nb_throws
        self.data = f"{self.nb_throws}d{self.type}"
        return self.data

    def roll(self, modifier: int = 0) -> int:
        """
        Roll the dice defined in the dice string.

        In case of several rolls, it sums the values of each roll and adds
        the modifier value (if any).

        Args:
            modifier (int): Positive or negative integer to add on a roll result.

        Returns:
            int: Sum of dice rolls results.
        """
        return sum(list(dice.roll(self.data))) + modifier
