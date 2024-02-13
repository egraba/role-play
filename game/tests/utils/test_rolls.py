import pytest

from character.tests.factories import CharacterFactory
from game.models.events import Roll, RollRequest
from game.tests.factories import RollRequestFactory
from game.utils.rolls import perform_roll


@pytest.mark.django_db
class TestPerformRoll:
    def test_perform_roll_success(self, monkeypatch):
        def patched_roll(modifier=0):
            return 10 + modifier

        monkeypatch.setattr("utils.dice.Dice.roll", patched_roll)

        character = CharacterFactory()
        request = RollRequestFactory(
            character=character,
            roll_type=RollRequest.RollType.ABILITY_CHECK,
            difficulty_class=RollRequest.DifficultyClass.EASY,
        )
        _, result = perform_roll(character, request)
        assert result == Roll.Result.SUCCESS

    def test_perform_roll_failure(self, monkeypatch):
        def patched_roll(modifier=0):
            return 10 + modifier

        monkeypatch.setattr("utils.dice.Dice.roll", patched_roll)

        character = CharacterFactory()
        request = RollRequestFactory(
            character=character,
            roll_type=RollRequest.RollType.ABILITY_CHECK,
            difficulty_class=RollRequest.DifficultyClass.HARD,
        )
        _, result = perform_roll(character, request)
        assert result == Roll.Result.FAILURE
