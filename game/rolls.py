from character.constants.abilities import AbilityName
from character.models.abilities import Ability, AbilityType
from character.models.character import Character
from utils.dice import Dice

from .constants.events import RollResultType
from .exceptions import InvalidRoll
from .models.combat import Fighter
from .models.events import RollRequest


def _roll(character: Character, ability_type: AbilityType) -> int:
    """
    Perform a roll and add proficiency bonus to the score,
    if the character is proficient in the ability passed as argument.
    """
    try:
        ability = character.abilities.get(ability_type=ability_type)
    except Ability.DoesNotExist:
        raise InvalidRoll(f"[{character}] does not have the ability: {ability_type}")
    score = Dice("d20").roll(ability.modifier)
    if character.is_proficient(ability):
        score += character.proficiency_bonus
    return score


def perform_roll(
    character: Character, request: RollRequest
) -> tuple[int, tuple[str, str]]:
    """
    Perform dice roll, according to DnD rules:
    - It adds proficiency bonus in case the character has the ability given in the roll request.
    - It adds or remove points in case the character has advantages or disadvantages.

    Args:
        character (Character): The character who performs the roll.
        request (RollRequest): The corresponding roll request from the master.

    Returns:
        tuple[int, tuple[str, str]]: Dice roll score and roll type result.
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
    if score >= request.difficulty_class:
        return score, RollResultType.SUCCESS
    return score, RollResultType.FAILURE


def perform_combat_initiative_roll(fighter: Fighter) -> int:
    dexterity = AbilityType.objects.get(name=AbilityName.DEXTERITY)
    score = _roll(fighter.character, dexterity)
    fighter.dexterity_check = score
    fighter.save()
    return score
