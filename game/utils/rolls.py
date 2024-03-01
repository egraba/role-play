from django.core.exceptions import ObjectDoesNotExist

from character.constants.races import SenseName
from character.exceptions import AbilityNotFound
from character.models.abilities import AbilityType
from character.models.character import Character
from utils.dice import Dice

from ..models.events import Roll, RollRequest


def _roll(character: Character, ability_type: AbilityType) -> int:
    try:
        ability = character.abilities.get(ability_type=ability_type)
    except ObjectDoesNotExist as exc:
        raise AbilityNotFound(ability_type) from exc

    score = Dice("d20").roll(ability.modifier)
    if character.is_proficient(ability):
        score += character.proficiency_bonus
    return score


def _has_advantage(
    character: Character, roll_type: RollRequest.RollType, against: str
) -> bool:
    """
    Indicate if a character has an advantage or not.

    Args:
        character (Character): The character who performs the roll.
        roll_type (RollRequest.RollType): The type of roll
        against (str): Against which attack the advantage is.

    Returns:
        bool: True if the character has an advantage, False otherwise.
    """
    has_dwarven_resilience = bool(
        character.senses.filter(name=SenseName.DWARVEN_RESILIENCE)
    )
    has_fey_ancestry = bool(character.senses.filter(name=SenseName.FEY_ANCESTRY))
    is_brave = bool(character.senses.filter(name=SenseName.BRAVE))

    if (
        has_dwarven_resilience
        and roll_type == RollRequest.RollType.SAVING_THROW
        and against == RollRequest.Against.POISON
    ):
        return True
    if (
        has_fey_ancestry
        and RollRequest.RollType.SAVING_THROW
        and against == RollRequest.Against.CHARM
    ):
        return True
    if (
        is_brave
        and RollRequest.RollType.SAVING_THROW
        and against == RollRequest.Against.BEING_FRIGHTENED
    ):
        return True
    return False


def _has_disadvantage(
    character: Character, roll_type: RollRequest.RollType, against: str
) -> bool:
    """
    Indicate if a character has a disadvantage or not.

    Args:
        character (Character): The character who performs the roll.
        roll_type (RollRequest.RollType): The type of roll
        against (str): Against which attack the disadvantage is.

    Returns:
        bool: True if the character has a disadvantage, False otherwise.
    """
    return False


def perform_roll(
    character: Character, request: RollRequest
) -> tuple[int, tuple[str, str]]:
    """
    Perform dice roll.

    Args:
        character (Character): The character who performs the roll.
        request (RollRequest): The corresponding roll request from the master.

    Returns:
        tuple[int, tuple[str, str]]: Dice roll score and roll type result.
    """

    score = _roll(character, request.ability_type)

    has_advantage = _has_advantage(character, request.roll_type, request.against)
    has_disadvantage = _has_disadvantage(character, request.roll_type, request.against)
    if has_advantage and has_disadvantage:
        # If the character has both advantage and disadantage, there is no more roll.
        pass
    else:
        new_score = _roll(character, request.ability_type)
        if has_advantage:
            score = max(score, new_score)
        if has_disadvantage:
            score = min(score, new_score)

    if score >= request.difficulty_class:
        return score, Roll.Result.SUCCESS
    return score, Roll.Result.FAILURE
