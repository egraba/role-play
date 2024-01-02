import re

DICE_REGEX = "(\d+)?d(\d+)([\+\-]\d+)?"

types = (4, 6, 8, 10, 12, 20)


class DiceFormatError(TypeError):
    """Raised when a dice string is wrongly formatted."""

    pass


class Dice(str):
    def add_throws(self, throws):
        """Add throws to a dice string.

        A dice string looks like 'NdT', where N is the number of throws
        and T the type of the dice.
        This method adds the throws passed as parameter to N.

        Args:
            dice_str (str): Dice string.

        """

        if not re.match(DICE_REGEX, self):
            raise DiceFormatError(f"[{self}] does not match a dice regex...")
        dice_str_parts = self.split("d")
        dice_type = int(dice_str_parts[1])
        if dice_type not in types:
            raise DiceFormatError("The provided dice type is not supported...")

        dice_str_parts[0] = str(int(dice_str_parts[0]) + throws)
        self = "d".join(dice_str_parts)
        return self
