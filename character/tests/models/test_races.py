import pytest

from character.models.races import Language


@pytest.mark.django_db(transaction=True)
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
