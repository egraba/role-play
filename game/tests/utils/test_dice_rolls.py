import pytest

from character.models.abilities import AbilityType
from character.tests.factories import (
    AbilityFactory,
    AbilityTypeFactory,
    CharacterFactory,
)
from game.models.events import AbilityCheck
from game.tests.factories import AbilityCheckRequestFactory
from game.utils.dice_rolls import perform_ability_check


@pytest.mark.django_db
class TestPerformAbilityCheck:
    def test_perform_ability_check(self):
        abilities = set()
        abilities.add(
            AbilityFactory(
                ability_type=AbilityTypeFactory(name=AbilityType.Name.CHARISMA)
            )
        )
        abilities.add(
            AbilityFactory(
                ability_type=AbilityTypeFactory(name=AbilityType.Name.CONSTITUTION)
            )
        )
        abilities.add(
            AbilityFactory(
                ability_type=AbilityTypeFactory(name=AbilityType.Name.DEXTERITY)
            )
        )
        abilities.add(
            AbilityFactory(
                ability_type=AbilityTypeFactory(name=AbilityType.Name.INTELLIGENCE)
            )
        )
        abilities.add(
            AbilityFactory(
                ability_type=AbilityTypeFactory(name=AbilityType.Name.STRENGTH)
            )
        )
        abilities.add(
            AbilityFactory(
                ability_type=AbilityTypeFactory(name=AbilityType.Name.WISDOM)
            )
        )
        character = CharacterFactory.create(abilities=abilities)
        ability_check_request = AbilityCheckRequestFactory(character=character)

        # Perform the test several time, as it uses random values.
        for _ in range(10):
            score, result = perform_ability_check(character, ability_check_request)
            if score >= ability_check_request.difficulty_class:
                assert result == AbilityCheck.Result.SUCCESS
            else:
                assert result == AbilityCheck.Result.FAILURE
