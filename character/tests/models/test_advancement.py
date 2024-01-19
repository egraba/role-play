import pytest

from character.models.advancement import Advancement


@pytest.mark.django_db
class TestAdvancementModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.advancement = Advancement.objects.last()

    def test_creation(self):
        assert isinstance(self.advancement, Advancement)

    def test_str(self):
        assert str(self.advancement) == str(self.advancement.level)
