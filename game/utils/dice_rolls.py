from character.models.character import Character
from utils.dice import Dice

from ..models.events import Roll, RollRequest


def perform_roll(
    character: Character, request: RollRequest
) -> tuple[int, tuple[str, str]]:
    """
    Perform dice roll.

    Args:
        character (Character): Character who performs the roll.
        request (RollRequest): The corresponding roll request from the master.

    Returns:
        tuple[int, tuple[str, str]]: Dice roll score and roll type result.
    """

    ability = character.abilities.get(ability_type=request.ability_type)
    score = Dice("d20").roll(ability.modifier)
    if score >= request.difficulty_class:
        return score, Roll.Result.SUCCESS
    return score, Roll.Result.FAILURE
