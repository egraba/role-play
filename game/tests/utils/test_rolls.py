import pytest

from character.constants.abilities import AbilityName
from character.models.abilities import AbilityType
from character.models.proficiencies import SavingThrowProficiency
from character.models.races import Sense
from character.tests.factories import CharacterFactory
from game.models.events import Roll, RollRequest
from game.tests.factories import RollRequestFactory
from game.utils.rolls import perform_roll


@pytest.mark.django_db
class TestPerformRoll:
    def test_perform_roll_success(self, monkeypatch):
        def patched_roll(self, modifier=0):
            return 10

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
        def patched_roll(self, modifier=0):
            return 10

        monkeypatch.setattr("utils.dice.Dice.roll", patched_roll)

        character = CharacterFactory()
        request = RollRequestFactory(
            character=character,
            roll_type=RollRequest.RollType.ABILITY_CHECK,
            difficulty_class=RollRequest.DifficultyClass.HARD,
        )
        _, result = perform_roll(character, request)
        assert result == Roll.Result.FAILURE

    def test_perform_roll_proficient(self, monkeypatch):
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
            roll_type=RollRequest.RollType.ABILITY_CHECK,
            difficulty_class=RollRequest.DifficultyClass.HARD,
        )
        score, _ = perform_roll(character, request)
        assert score == 12

    def test_perform_roll_with_advantage_dwarven_resistance(self, monkeypatch):
        score_generator = (score for score in range(10, 20, 5))

        def patched_roll(self, modifier=0):
            return next(score_generator)

        monkeypatch.setattr("utils.dice.Dice.roll", patched_roll)

        character = CharacterFactory()
        character.senses.add(Sense.objects.get(name=Sense.Name.DWARVEN_RESILIENCE))
        character.save()
        request = RollRequestFactory(
            character=character,
            roll_type=RollRequest.RollType.SAVING_THROW,
            difficulty_class=RollRequest.DifficultyClass.EASY,
            against=RollRequest.Against.POISON,
        )
        score, _ = perform_roll(character, request)
        assert score == 15

    def test_perform_roll_with_advantage_fey_ancestry(self, monkeypatch):
        score_generator = (score for score in range(10, 20, 5))

        def patched_roll(self, modifier=0):
            return next(score_generator)

        monkeypatch.setattr("utils.dice.Dice.roll", patched_roll)

        character = CharacterFactory()
        character.senses.add(Sense.objects.get(name=Sense.Name.FEY_ANCESTRY))
        character.save()
        request = RollRequestFactory(
            character=character,
            roll_type=RollRequest.RollType.SAVING_THROW,
            difficulty_class=RollRequest.DifficultyClass.EASY,
            against=RollRequest.Against.CHARM,
        )
        score, _ = perform_roll(character, request)
        assert score == 15

    def test_perform_roll_with_advantage_brave(self, monkeypatch):
        score_generator = (score for score in range(10, 20, 5))

        def patched_roll(self, modifier=0):
            return next(score_generator)

        monkeypatch.setattr("utils.dice.Dice.roll", patched_roll)

        character = CharacterFactory()
        character.senses.add(Sense.objects.get(name=Sense.Name.BRAVE))
        character.save()
        request = RollRequestFactory(
            character=character,
            roll_type=RollRequest.RollType.SAVING_THROW,
            difficulty_class=RollRequest.DifficultyClass.EASY,
            against=RollRequest.Against.BEING_FRIGHTENED,
        )
        score, _ = perform_roll(character, request)
        assert score == 15
