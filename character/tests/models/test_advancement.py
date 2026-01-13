import pytest

from character.models.advancement import Advancement


@pytest.mark.django_db
class TestAdvancementModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.advancement, _ = Advancement.objects.get_or_create(
            level=1, defaults={"xp": 0, "proficiency_bonus": 2}
        )

    def test_creation(self):
        assert isinstance(self.advancement, Advancement)

    def test_str(self):
        assert str(self.advancement) == str(self.advancement.level)
