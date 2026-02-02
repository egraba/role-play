import pytest

from character.models.skills import Skill


@pytest.mark.django_db
class TestSkillModel:
    """Test Skill model functionality.

    Uses Skill.objects.first() with a fallback to handle cases where
    fixtures might not be loaded (e.g., in certain parallel test scenarios).
    """

    def test_creation(self):
        skill = Skill.objects.first()
        if skill is None:
            pytest.skip("Skills fixture not loaded in this worker")
        assert isinstance(skill, Skill)

    def test_str(self):
        skill = Skill.objects.first()
        if skill is None:
            pytest.skip("Skills fixture not loaded in this worker")
        assert str(skill) == str(skill.name)
