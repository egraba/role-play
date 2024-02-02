import pytest

from character.tests.factories import CharacterFactory
from game.models.events import AbilityCheck
from game.tests.factories import AbilityCheckRequestFactory
from game.utils.dice_rolls import perform_ability_check


@pytest.mark.django_db
def test_perform_ability_check():
    character = CharacterFactory()
    ability_check_request = AbilityCheckRequestFactory(character=character)
    # Perform the test several time, as it uses random values.
    for _ in range(10):
        score, result = perform_ability_check(character, ability_check_request)
        if score >= ability_check_request.difficulty_class:
            assert result == AbilityCheck.Result.SUCCESS
        else:
            assert result == AbilityCheck.Result.FAILURE
