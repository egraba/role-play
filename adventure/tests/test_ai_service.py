"""Tests for the AI generation service."""

from unittest.mock import MagicMock, patch

import pytest

from adventure.services.ai import (
    AIGenerationError,
    _get_api_key,
    generate_campaign_synopsis,
    generate_scene_description,
)
from adventure.tests.factories import CampaignFactory, SceneFactory
from user.tests.factories import UserFactory


@pytest.mark.django_db
def test_get_api_key_raises_when_not_set() -> None:
    user = UserFactory()
    assert user.anthropic_api_key == ""
    with pytest.raises(AIGenerationError):
        _get_api_key(user)


@pytest.mark.django_db
def test_get_api_key_returns_key_when_set() -> None:
    user = UserFactory()
    user.anthropic_api_key = "sk-ant-test"
    user.save()
    key = _get_api_key(user)
    assert key == "sk-ant-test"


@pytest.mark.django_db
@patch("adventure.services.ai._call_claude")
def test_generate_campaign_synopsis(mock_claude: MagicMock) -> None:
    mock_claude.return_value = "A thrilling campaign awaits."
    user = UserFactory()
    user.anthropic_api_key = "sk-ant-test"
    user.save()
    campaign = CampaignFactory(owner=user, main_conflict="Evil dragon", party_level=5)
    result = generate_campaign_synopsis(user, campaign)
    assert result == "A thrilling campaign awaits."
    mock_claude.assert_called_once()


@pytest.mark.django_db
@patch("adventure.services.ai._call_claude")
def test_generate_scene_description(mock_claude: MagicMock) -> None:
    mock_claude.return_value = "A dark dungeon corridor."
    user = UserFactory()
    user.anthropic_api_key = "sk-ant-test"
    user.save()
    scene = SceneFactory()
    result = generate_scene_description(user, scene)
    assert result == "A dark dungeon corridor."
    mock_claude.assert_called_once()
