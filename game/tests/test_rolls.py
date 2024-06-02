import pytest

from character.constants.abilities import AbilityName
from character.tests.factories import CharacterFactory
from game.constants.events import Against, DifficultyClass, RollResult, RollType
from game.tests.factories import RollRequestFactory
from game.rolls import perform_roll

pytestmark = pytest.mark.django_db


def test_perform_roll_success(monkeypatch):
    def patched_roll(self, modifier=0):
        return 10

    monkeypatch.setattr("utils.dice.Dice.roll", patched_roll)

    character = CharacterFactory()
    request = RollRequestFactory(
        character=character,
        roll_type=RollType.ABILITY_CHECK,
        difficulty_class=DifficultyClass.EASY,
    )
    _, result = perform_roll(character, request)
    assert result == RollResult.SUCCESS


def test_perform_roll_failure(monkeypatch):
    def patched_roll(self, modifier=0):
        return 10

    monkeypatch.setattr("utils.dice.Dice.roll", patched_roll)

    character = CharacterFactory()
    request = RollRequestFactory(
        character=character,
        roll_type=RollType.ABILITY_CHECK,
        difficulty_class=DifficultyClass.HARD,
    )
    _, result = perform_roll(character, request)
    assert result == RollResult.FAILURE


def test_perform_roll_with_proficiency(monkeypatch):
    def patched_roll(self, modifier=0):
        return 10

    def patched_is_proficient(self, ability):
        return True

    monkeypatch.setattr("utils.dice.Dice.roll", patched_roll)
    monkeypatch.setattr(
        "character.models.character.Character.is_proficient", patched_is_proficient
    )

    character = CharacterFactory()
    request = RollRequestFactory(
        character=character,
        ability_type=AbilityName.CHARISMA,
        roll_type=RollType.ABILITY_CHECK,
        difficulty_class=DifficultyClass.HARD,
    )
    score, _ = perform_roll(character, request)
    assert score == 12


def test_perform_roll_with_advantage(monkeypatch):
    score_generator = (score for score in range(10, 20, 5))

    def patched_roll(self, modifier=0):
        return next(score_generator)

    def patched_advantage(self, roll_type, against):
        return True

    monkeypatch.setattr("utils.dice.Dice.roll", patched_roll)
    monkeypatch.setattr(
        "character.models.character.Character.has_advantage", patched_advantage
    )

    character = CharacterFactory()
    request = RollRequestFactory(
        character=character,
        roll_type=RollType.SAVING_THROW,
        difficulty_class=DifficultyClass.EASY,
        against=Against.POISON,
    )
    score, _ = perform_roll(character, request)
    assert score == 15
