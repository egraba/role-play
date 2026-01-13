import pytest

from character.constants.abilities import AbilityName
from game.constants.events import Against, DifficultyClass, RollResultType, RollType
from game.exceptions import InvalidRoll
from game.tests.factories import RollRequestFactory, PlayerFactory
from game.rolls import _roll, perform_roll

pytestmark = pytest.mark.django_db


def test_perform_roll_success(monkeypatch):
    def patched_roll(self, modifier=0):
        return 10

    monkeypatch.setattr("utils.dice.DiceString.roll", patched_roll)
    player = PlayerFactory()
    request = RollRequestFactory(
        player=player,
        roll_type=RollType.ABILITY_CHECK,
        difficulty_class=DifficultyClass.EASY,
    )
    _, result = perform_roll(player, request)
    assert result == RollResultType.SUCCESS


def test_perform_roll_failure(monkeypatch):
    def patched_roll(self, modifier=0):
        return 10

    monkeypatch.setattr("utils.dice.DiceString.roll", patched_roll)
    player = PlayerFactory()
    request = RollRequestFactory(
        player=player,
        roll_type=RollType.ABILITY_CHECK,
        difficulty_class=DifficultyClass.HARD,
    )
    _, result = perform_roll(player, request)
    assert result == RollResultType.FAILURE


def test_perform_roll_with_proficiency(monkeypatch):
    def patched_roll(self, modifier=0):
        return 10

    def patched_is_proficient(self, ability):
        return True

    monkeypatch.setattr("utils.dice.DiceString.roll", patched_roll)
    monkeypatch.setattr(
        "character.models.character.Character.is_proficient", patched_is_proficient
    )
    player = PlayerFactory()
    request = RollRequestFactory(
        player=player,
        ability_type=AbilityName.CHARISMA,
        roll_type=RollType.ABILITY_CHECK,
        difficulty_class=DifficultyClass.HARD,
    )
    score, _ = perform_roll(player, request)
    assert score == 12


def test_perform_roll_with_advantage(monkeypatch):
    score_generator = (score for score in range(10, 20, 5))

    def patched_roll(self, modifier=0):
        return next(score_generator)

    def patched_advantage(self, roll_type, against):
        return True

    monkeypatch.setattr("utils.dice.DiceString.roll", patched_roll)
    monkeypatch.setattr(
        "character.models.character.Character.has_advantage", patched_advantage
    )
    player = PlayerFactory()
    request = RollRequestFactory(
        player=player,
        roll_type=RollType.SAVING_THROW,
        difficulty_class=DifficultyClass.EASY,
        against=Against.POISON,
    )
    score, _ = perform_roll(player, request)
    assert score == 15


def test_perform_roll_with_disadvantage(monkeypatch):
    """Test that disadvantage takes the lower of two rolls."""
    score_generator = (score for score in [15, 10])

    def patched_roll(self, modifier=0):
        return next(score_generator)

    def patched_disadvantage(self, roll_type, against):
        return True

    monkeypatch.setattr("utils.dice.DiceString.roll", patched_roll)
    monkeypatch.setattr(
        "character.models.character.Character.has_disadvantage", patched_disadvantage
    )
    player = PlayerFactory()
    request = RollRequestFactory(
        player=player,
        roll_type=RollType.SAVING_THROW,
        difficulty_class=DifficultyClass.EASY,
        against=Against.POISON,
    )
    score, _ = perform_roll(player, request)
    assert score == 10  # Takes the lower roll


def test_perform_roll_with_both_advantage_and_disadvantage(monkeypatch):
    """Test that having both advantage and disadvantage cancels out - no second roll."""
    roll_count = 0

    def patched_roll(self, modifier=0):
        nonlocal roll_count
        roll_count += 1
        return 10

    def patched_advantage(self, roll_type, against):
        return True

    def patched_disadvantage(self, roll_type, against):
        return True

    monkeypatch.setattr("utils.dice.DiceString.roll", patched_roll)
    monkeypatch.setattr(
        "character.models.character.Character.has_advantage", patched_advantage
    )
    monkeypatch.setattr(
        "character.models.character.Character.has_disadvantage", patched_disadvantage
    )
    player = PlayerFactory()
    request = RollRequestFactory(
        player=player,
        roll_type=RollType.ABILITY_CHECK,
        difficulty_class=DifficultyClass.EASY,
    )
    score, _ = perform_roll(player, request)
    assert score == 10
    assert roll_count == 1  # Only one roll when advantage and disadvantage cancel out


def test_roll_invalid_ability(monkeypatch):
    """Test that _roll raises InvalidRoll when character doesn't have the ability."""
    from character.models.abilities import AbilityType

    player = PlayerFactory()
    # Clear all abilities from the character
    player.character.abilities.all().delete()

    ability_type = AbilityType.objects.first()
    with pytest.raises(InvalidRoll) as exc_info:
        _roll(player, ability_type)
    assert "does not have the ability" in str(exc_info.value)
