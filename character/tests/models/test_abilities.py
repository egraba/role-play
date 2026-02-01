import pytest

from character.models.abilities import Ability, AbilityType

from ..factories import AbilityFactory, AbilityTypeFactory


@pytest.mark.django_db
class TestAbilityTypeModel:
    ability_type = None

    @pytest.fixture(autouse=True)
    def setup(self):
        self.ability_type = AbilityTypeFactory()

    def test_creation(self):
        assert isinstance(self.ability_type, AbilityType)

    def test_str(self):
        assert str(self.ability_type) == str(self.ability_type.name)


@pytest.mark.django_db
class TestAbilityModel:
    ability = None

    @pytest.fixture(autouse=True)
    def setup(self):
        self.ability = AbilityFactory()

    def test_creation(self):
        assert isinstance(self.ability, Ability)

    def test_str(self):
        assert str(self.ability) == str(self.ability.ability_type.name)
