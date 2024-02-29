import pytest

from character.models.classes import ClassAdvancement


@pytest.mark.django_db
class TestClassAdvancementModel:
    class_advancement = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.class_advancement = ClassAdvancement.objects.last()

    def test_creation(self):
        assert isinstance(self.class_advancement, ClassAdvancement)

    def test_str(self):
        assert str(self.class_advancement) == str(self.class_advancement.level)
