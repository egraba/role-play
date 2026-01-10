import pytest

from character.constants.conditions import ConditionName
from character.models.conditions import CharacterCondition

from ..factories import CharacterFactory, ConditionFactory


@pytest.mark.django_db
class TestConditionModel:
    def test_creation(self):
        condition = ConditionFactory(
            name=ConditionName.POISONED,
            description="A poisoned creature has disadvantage.",
        )
        assert condition.name == ConditionName.POISONED
        assert "poisoned" in condition.description.lower()

    def test_str(self):
        condition = ConditionFactory(name=ConditionName.BLINDED)
        assert str(condition) == "Blinded"

    def test_all_conditions_valid(self):
        """Verify all ConditionName choices are valid."""
        for name, _ in ConditionName.choices:
            condition = ConditionFactory(name=name)
            assert condition.name == name


@pytest.mark.django_db
class TestCharacterConditionModel:
    @pytest.fixture
    def character(self):
        return CharacterFactory()

    @pytest.fixture
    def condition(self):
        return ConditionFactory(name=ConditionName.POISONED)

    def test_creation(self, character, condition):
        char_condition = CharacterCondition.objects.create(
            character=character, condition=condition
        )
        assert char_condition.character == character
        assert char_condition.condition == condition
        assert char_condition.exhaustion_level is None

    def test_str_regular_condition(self, character, condition):
        char_condition = CharacterCondition.objects.create(
            character=character, condition=condition
        )
        assert str(char_condition) == "Poisoned"

    def test_str_exhaustion_with_level(self, character):
        exhaustion = ConditionFactory(name=ConditionName.EXHAUSTION)
        char_condition = CharacterCondition.objects.create(
            character=character, condition=exhaustion, exhaustion_level=3
        )
        assert str(char_condition) == "Exhaustion (Level 3)"

    def test_exhaustion_levels(self, character):
        """Test exhaustion can have levels 1-6."""
        exhaustion = ConditionFactory(name=ConditionName.EXHAUSTION)
        for level in range(1, 7):
            char_condition = CharacterCondition.objects.create(
                character=character, condition=exhaustion, exhaustion_level=level
            )
            assert char_condition.exhaustion_level == level
            char_condition.delete()

    def test_unique_together_constraint(self, character, condition):
        """A character can only have one instance of each condition."""
        CharacterCondition.objects.create(character=character, condition=condition)
        with pytest.raises(Exception):  # IntegrityError
            CharacterCondition.objects.create(character=character, condition=condition)

    def test_character_active_conditions_relation(self, character, condition):
        """Test the related_name 'active_conditions' works."""
        CharacterCondition.objects.create(character=character, condition=condition)
        assert character.active_conditions.count() == 1
        assert character.active_conditions.first().condition == condition

    def test_multiple_conditions_on_character(self, character):
        """A character can have multiple different conditions."""
        poisoned = ConditionFactory(name=ConditionName.POISONED)
        blinded = ConditionFactory(name=ConditionName.BLINDED)
        prone = ConditionFactory(name=ConditionName.PRONE)

        CharacterCondition.objects.create(character=character, condition=poisoned)
        CharacterCondition.objects.create(character=character, condition=blinded)
        CharacterCondition.objects.create(character=character, condition=prone)

        assert character.active_conditions.count() == 3

    def test_cascade_delete_on_character(self, character, condition):
        """CharacterCondition should be deleted when character is deleted."""
        CharacterCondition.objects.create(character=character, condition=condition)
        character_id = character.id
        character.delete()
        assert not CharacterCondition.objects.filter(character_id=character_id).exists()

    def test_cascade_delete_on_condition(self, character, condition):
        """CharacterCondition should be deleted when condition is deleted."""
        CharacterCondition.objects.create(character=character, condition=condition)
        condition_name = condition.name
        condition.delete()
        assert not CharacterCondition.objects.filter(
            condition_id=condition_name
        ).exists()
