from character.models.abilities import AbilityType, Ability
from character.models.character import Character
from utils.dice import Dice

from .constants.events import RollResult
from .models.events import RollRequest
from .exceptions import RollInvalid


def _roll(character: Character, ability_type: AbilityType) -> int:
    """
    Perform a roll and add proficiency bonus to the score,
    if the character is proficient in the ability passed as argument.
    """
    try:
        ability = character.abilities.get(ability_type=ability_type)
    except Ability.DoesNotExist:
        raise RollInvalid(f"[{character}] does not have the ability: {ability_type}")
    score = Dice("d20").roll(ability.modifier)
    if character.is_proficient(ability):
        score += character.proficiency_bonus
    return score


def perform_roll(
    character: Character, request: RollRequest
) -> tuple[int, tuple[str, str] | None]:
    """
    Perform dice roll, according to DnD rules:
    - It adds proficiency bonus in case the character has the ability given in the roll request.
    - It adds or remove points in case the character has advantages or disadvantages.

    Args:
        character (Character): The character who performs the roll.
        request (RollRequest): The corresponding roll request from the master.

    Returns:
        tuple[int, tuple[str, str] | None]: Dice roll score and roll type result (if any).
    """

    score = _roll(character, request.ability_type)
    has_advantage = character.has_advantage(request.roll_type, request.against)
    has_disadvantage = character.has_disadvantage(request.roll_type, request.against)
    if has_advantage and has_disadvantage:
        # If the character has both advantage and disadantage, there is no more roll.
        pass
    else:
        new_score = _roll(character, request.ability_type)
        if has_advantage:
            score = max(score, new_score)
        if has_disadvantage:
            score = min(score, new_score)
    if request.is_combat:
        fighter = character.fighter
        fighter.dexterity_check = score
        fighter.save()
    if request.difficulty_class is None:
        # There is no difficulty class, in some cases.
        # For instance, in a combat, the Master asks fighters to perform a dextery check,
        # to get the order of the fighters. Therefore, no success nor failure is expected.
        return score, None
    if score >= request.difficulty_class:
        return score, RollResult.SUCCESS
    return score, RollResult.FAILURE
