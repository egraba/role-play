from character.models.character import Character
from utils.dice import Dice

from ..models.events import AbilityCheck, AbilityCheckRequest


def perform_ability_check(
    character: Character, request: AbilityCheckRequest
) -> tuple[int, tuple[str, str]]:
    """
    Perform ability check.

    Args:
        character (Character): Character who performs the ability check.
        request (AbilityCheckRequest): The corresponding ability check request from the master (DM).

    Returns:
        tuple[int, tuple[str, str]]: Dice roll score and ability check result.
    """

    ability = character.abilities.get(ability_type=request.ability_type)
    score = Dice("d20").roll(ability.modifier)
    if score >= request.difficulty_class:
        return score, AbilityCheck.Result.SUCCESS
    else:
        return score, AbilityCheck.Result.FAILURE
