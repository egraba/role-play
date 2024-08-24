import pytest

from character.models.races import Language, Sense


@pytest.mark.django_db
class TestLanguageModel:
    language = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.language = Language.objects.last()

    def test_creation(self):
        assert isinstance(self.language, Language)

    def test_str(self):
        assert str(self.language) == self.language.name


@pytest.mark.django_db
class TestAbilityModel:
    ability = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.ability = Sense.objects.last()

    def test_creation(self):
        assert isinstance(self.ability, Sense)

    def test_str(self):
        assert str(self.ability) == self.ability.name
