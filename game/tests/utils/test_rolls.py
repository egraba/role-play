import pytest

from character.constants.abilities import AbilityName
from character.constants.races import SenseName
from character.models.abilities import AbilityType
from character.models.proficiencies import SavingThrowProficiency
from character.models.races import Sense
from character.tests.factories import CharacterFactory
from game.constants.events import Against, DifficultyClass, RollResult, RollType
from game.tests.factories import RollRequestFactory
from game.utils.rolls import perform_roll

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


def test_perform_roll_proficient(monkeypatch):
    def patched_roll(self, modifier=0):
        return 10

    monkeypatch.setattr("utils.dice.Dice.roll", patched_roll)

    character = CharacterFactory()
    SavingThrowProficiency.objects.create(
        character=character,
        ability_type=AbilityType.objects.get(name=AbilityName.CHARISMA),
    )
    request = RollRequestFactory(
        character=character,
        ability_type=AbilityName.CHARISMA,
        roll_type=RollType.ABILITY_CHECK,
        difficulty_class=DifficultyClass.HARD,
    )
    score, _ = perform_roll(character, request)
    assert score == 12


def test_perform_roll_with_advantage_dwarven_resistance(monkeypatch):
    score_generator = (score for score in range(10, 20, 5))

    def patched_roll(modifier=0):
        return next(score_generator)

    monkeypatch.setattr("utils.dice.Dice.roll", patched_roll)

    character = CharacterFactory()
    character.senses.add(Sense.objects.get(name=SenseName.DWARVEN_RESILIENCE))
    character.save()
    request = RollRequestFactory(
        character=character,
        roll_type=RollType.SAVING_THROW,
        difficulty_class=DifficultyClass.EASY,
        against=Against.POISON,
    )
    score, _ = perform_roll(character, request)
    assert score == 15


def test_perform_roll_with_advantage_fey_ancestry(monkeypatch):
    score_generator = (score for score in range(10, 20, 5))

    def patched_roll(modifier=0):
        return next(score_generator)

    monkeypatch.setattr("utils.dice.Dice.roll", patched_roll)

    character = CharacterFactory()
    character.senses.add(Sense.objects.get(name=SenseName.FEY_ANCESTRY))
    character.save()
    request = RollRequestFactory(
        character=character,
        roll_type=RollType.SAVING_THROW,
        difficulty_class=DifficultyClass.EASY,
        against=Against.CHARM,
    )
    score, _ = perform_roll(character, request)
    assert score == 15


def test_perform_roll_with_advantage_brave(monkeypatch):
    score_generator = (score for score in range(10, 20, 5))

    def patched_roll(modifier=0):
        return next(score_generator)

    monkeypatch.setattr("utils.dice.Dice.roll", patched_roll)

    character = CharacterFactory()
    character.senses.add(Sense.objects.get(name=SenseName.BRAVE))
    character.save()
    request = RollRequestFactory(
        character=character,
        roll_type=RollType.SAVING_THROW,
        difficulty_class=DifficultyClass.EASY,
        against=Against.BEING_FRIGHTENED,
    )
    score, _ = perform_roll(character, request)
    assert score == 15
