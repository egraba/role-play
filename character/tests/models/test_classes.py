import pytest

from character.models.klasses import KlassAdvancement


@pytest.mark.django_db
class TestClassAdvancementModel:
    klass_advancement = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.klass_advancement = KlassAdvancement.objects.last()

    def test_creation(self):
        assert isinstance(self.klass_advancement, KlassAdvancement)

    def test_str(self):
        assert str(self.klass_advancement) == str(self.klass_advancement.level)
