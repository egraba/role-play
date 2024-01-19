import pytest

from character.models.abilities import Ability, AbilityScoreIncrease, AbilityType

from ..factories import AbilityFactory, AbilityScoreIncreaseFactory


@pytest.mark.django_db
class TestAbilityTypeModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.ability_type = AbilityType.objects.last()

    def test_creation(self):
        assert isinstance(self.ability_type, AbilityType)

    def test_str(self):
        assert str(self.ability_type) == str(self.ability_type.name)


@pytest.mark.django_db
class TestAbilityModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.ability = AbilityFactory()

    def test_creation(self):
        assert isinstance(self.ability, Ability)

    def test_str(self):
        assert str(self.ability) == str(self.ability.ability_type.name)


@pytest.mark.django_db
class TestAbilityScoreIncreaseModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.ability_score_increase = AbilityScoreIncreaseFactory()

    def test_creation(self):
        assert isinstance(self.ability_score_increase, AbilityScoreIncrease)
