import random
import re
from collections import UserString

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
        data (str): The dice string itself, inherited from Userstring class.
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
        self.dice_type = dice_type

    def _roll_dice(self) -> list[int]:
        """Roll the dice and return individual results."""
        return [random.randint(1, self.dice_type) for _ in range(self.nb_throws)]

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
        self.nb_throws += nb_throws
        self.data = f"{self.nb_throws}d{self.dice_type}"
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
        return sum(self._roll_dice()) + modifier

    def roll_keeping_individual(self, modifier: int = 0) -> tuple[int, list[int]]:
        """Roll and return individual die results for transparency.

        Args:
            modifier (int): Positive or negative integer to add to the total.

        Returns:
            tuple: (total_with_modifier, list_of_individual_rolls)
        """
        rolls = self._roll_dice()
        return sum(rolls) + modifier, rolls

    def roll_with_advantage(self, modifier: int = 0) -> tuple[int, int, int]:
        """Roll twice and take the higher result (D&D 5e advantage).

        Args:
            modifier (int): Positive or negative integer to add to the result.

        Returns:
            tuple: (final_result_with_modifier, first_roll, second_roll)
        """
        roll1 = sum(self._roll_dice())
        roll2 = sum(self._roll_dice())
        return max(roll1, roll2) + modifier, roll1, roll2

    def roll_with_disadvantage(self, modifier: int = 0) -> tuple[int, int, int]:
        """Roll twice and take the lower result (D&D 5e disadvantage).

        Args:
            modifier (int): Positive or negative integer to add to the result.

        Returns:
            tuple: (final_result_with_modifier, first_roll, second_roll)
        """
        roll1 = sum(self._roll_dice())
        roll2 = sum(self._roll_dice())
        return min(roll1, roll2) + modifier, roll1, roll2

    def roll_damage(self, critical: bool = False) -> int:
        """Roll damage dice with optional critical hit (doubles dice).

        Args:
            critical: If True, roll twice as many dice (D&D 5e critical hit).

        Returns:
            int: Total damage rolled.
        """
        rolls = self._roll_dice()
        if critical:
            rolls += self._roll_dice()
        return sum(rolls)


def roll_d20_test(
    modifier: int = 0,
    advantage: bool = False,
    disadvantage: bool = False,
) -> tuple[int, bool, bool]:
    """Perform a d20 ability check or saving throw.

    Handles advantage/disadvantage and detects natural 1s and 20s.
    If both advantage and disadvantage apply, they cancel out.

    Args:
        modifier: Bonus/penalty to add to the roll.
        advantage: Roll twice, take higher.
        disadvantage: Roll twice, take lower.

    Returns:
        tuple: (total, is_natural_20, is_natural_1)
    """
    d20 = DiceString("d20")

    if advantage and disadvantage:
        # Cancel out - single roll
        _, rolls = d20.roll_keeping_individual()
        natural = rolls[0]
    elif advantage:
        _, roll1, roll2 = d20.roll_with_advantage()
        natural = max(roll1, roll2)
    elif disadvantage:
        _, roll1, roll2 = d20.roll_with_disadvantage()
        natural = min(roll1, roll2)
    else:
        _, rolls = d20.roll_keeping_individual()
        natural = rolls[0]

    return natural + modifier, natural == 20, natural == 1
