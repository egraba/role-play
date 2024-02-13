import pytest

from character.tests.factories import CharacterFactory
from game.models.events import Roll, RollRequest
from game.tests.factories import RollRequestFactory
from game.utils.rolls import perform_roll


@pytest.mark.django_db
def test_perform_roll():
    character = CharacterFactory()
    request = RollRequestFactory(
        character=character, roll_type=RollRequest.RollType.ABILITY_CHECK
    )
    # Perform the test several time, as it uses random values.
    for _ in range(10):
        score, result = perform_roll(character, request)
        if score >= request.difficulty_class:
            assert result == Roll.Result.SUCCESS
        else:
            assert result == Roll.Result.FAILURE
