import pytest
from django.urls import reverse

from ..factories import CharacterFactory


@pytest.fixture
def skills_character(client):
    """Create a test character for skills tests."""
    char = CharacterFactory()
    client.force_login(char.user)
    return char


@pytest.mark.django_db
class TestSkillsPanelView:
    """Test skills panel HTMX view."""

    def test_skills_panel_view(self, client, skills_character):
        url = reverse("character-skills-panel", args=[skills_character.pk])
        response = client.get(url)
        assert response.status_code == 200
        assert b"skills-panel-component" in response.content

    def test_skills_panel_shows_all_skills(self, client, skills_character):
        url = reverse("character-skills-panel", args=[skills_character.pk])
        response = client.get(url)
        # Check for some standard D&D skills
        assert b"Acrobatics" in response.content
        assert b"Athletics" in response.content
        assert b"Perception" in response.content
        assert b"Stealth" in response.content

    def test_skills_panel_shows_filter_buttons(self, client, skills_character):
        url = reverse("character-skills-panel", args=[skills_character.pk])
        response = client.get(url)
        assert b"filter-btn" in response.content
        assert b"All" in response.content

    def test_skills_panel_filter_by_ability(self, client, skills_character):
        url = reverse("character-skills-panel", args=[skills_character.pk])
        response = client.get(url, {"ability": "DEX"})
        assert response.status_code == 200
        # DEX skills should be present
        assert b"Acrobatics" in response.content
        assert b"Stealth" in response.content
        # STR skills should not be present when filtering by DEX
        assert b"Athletics" not in response.content

    def test_skills_panel_invalid_filter_ignored(self, client, skills_character):
        url = reverse("character-skills-panel", args=[skills_character.pk])
        response = client.get(url, {"ability": "INVALID"})
        assert response.status_code == 200
        # Should show all skills when filter is invalid
        assert b"Acrobatics" in response.content
        assert b"Athletics" in response.content

    def test_skills_panel_shows_roll_buttons(self, client, skills_character):
        url = reverse("character-skills-panel", args=[skills_character.pk])
        response = client.get(url)
        assert b"skill-roll-btn" in response.content

    def test_skills_panel_requires_login(self, client, skills_character):
        client.logout()
        url = reverse("character-skills-panel", args=[skills_character.pk])
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login


@pytest.mark.django_db
class TestSkillRollView:
    """Test skill roll HTMX view."""

    def test_skill_roll_returns_result(self, client, skills_character):
        url = reverse("character-skill-roll", args=[skills_character.pk])
        response = client.post(url, {"skill": "Perception", "modifier": "3"})
        assert response.status_code == 200
        assert b"roll-result-content" in response.content
        assert b"Perception Check" in response.content

    def test_skill_roll_shows_breakdown(self, client, skills_character):
        url = reverse("character-skill-roll", args=[skills_character.pk])
        response = client.post(url, {"skill": "Stealth", "modifier": "5"})
        assert response.status_code == 200
        assert b"roll-result-breakdown" in response.content
        assert b"d20(" in response.content

    def test_skill_roll_handles_negative_modifier(self, client, skills_character):
        url = reverse("character-skill-roll", args=[skills_character.pk])
        response = client.post(url, {"skill": "Athletics", "modifier": "-2"})
        assert response.status_code == 200
        assert b"-2" in response.content

    def test_skill_roll_handles_invalid_modifier(self, client, skills_character):
        url = reverse("character-skill-roll", args=[skills_character.pk])
        response = client.post(url, {"skill": "Perception", "modifier": "invalid"})
        assert response.status_code == 200
        # Should default to 0 modifier

    def test_skill_roll_requires_login(self, client, skills_character):
        client.logout()
        url = reverse("character-skill-roll", args=[skills_character.pk])
        response = client.post(url, {"skill": "Perception", "modifier": "3"})
        assert response.status_code == 302  # Redirect to login
