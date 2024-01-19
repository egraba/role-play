import pytest

from character.models.skills import Skill


@pytest.mark.django_db
class TestSkillModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.skill = Skill.objects.last()

    def test_creation(self):
        assert isinstance(self.skill, Skill)

    def test_str(self):
        assert str(self.skill) == str(self.skill.name)
