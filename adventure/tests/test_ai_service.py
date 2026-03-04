"""Tests for the AI generation service."""

from unittest.mock import MagicMock, patch

import pytest

from adventure.exceptions import AIGenerationError
from adventure.tests.factories import (
    ActFactory,
    CampaignFactory,
    EncounterFactory,
    LocationFactory,
    NPCFactory,
    SceneFactory,
)
from ai.adventure import (
    _call_claude,
    _get_api_key,
    generate_act_summary,
    generate_campaign_synopsis,
    generate_encounter_description,
    generate_location_description,
    generate_npc_personality,
    generate_scene_description,
)
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
@patch("ai.adventure._call_claude")
def test_generate_campaign_synopsis(mock_claude: MagicMock) -> None:
    mock_claude.return_value = "A thrilling campaign awaits."
    user = UserFactory(anthropic_api_key="sk-ant-test")
    campaign = CampaignFactory(owner=user, main_conflict="Evil dragon", party_level=5)
    result = generate_campaign_synopsis(user, campaign)
    assert result == "A thrilling campaign awaits."
    mock_claude.assert_called_once()


@pytest.mark.django_db
@patch("ai.adventure._call_claude")
def test_generate_scene_description(mock_claude: MagicMock) -> None:
    mock_claude.return_value = "A dark dungeon corridor."
    user = UserFactory(anthropic_api_key="sk-ant-test")
    scene = SceneFactory()
    result = generate_scene_description(user, scene)
    assert result == "A dark dungeon corridor."
    mock_claude.assert_called_once()


@pytest.mark.django_db
@patch("ai.adventure._call_claude")
def test_generate_act_summary(mock_claude: MagicMock) -> None:
    mock_claude.return_value = "Act summary text."
    user = UserFactory(anthropic_api_key="sk-ant-test")
    act = ActFactory()
    result = generate_act_summary(user, act)
    assert result == "Act summary text."
    mock_claude.assert_called_once()


@pytest.mark.django_db
@patch("ai.adventure._call_claude")
def test_generate_npc_personality(mock_claude: MagicMock) -> None:
    mock_claude.return_value = "Personality: Gruff and taciturn."
    user = UserFactory(anthropic_api_key="sk-ant-test")
    npc = NPCFactory()
    result = generate_npc_personality(user, npc)
    assert result == "Personality: Gruff and taciturn."
    mock_claude.assert_called_once()


@pytest.mark.django_db
@patch("ai.adventure._call_claude")
def test_generate_location_description(mock_claude: MagicMock) -> None:
    mock_claude.return_value = "A fog-shrouded swamp."
    user = UserFactory(anthropic_api_key="sk-ant-test")
    location = LocationFactory()
    result = generate_location_description(user, location)
    assert result == "A fog-shrouded swamp."
    mock_claude.assert_called_once()


@pytest.mark.django_db
@patch("ai.adventure._call_claude")
def test_generate_encounter_description(mock_claude: MagicMock) -> None:
    mock_claude.return_value = "Goblins ambush the party."
    user = UserFactory(anthropic_api_key="sk-ant-test")
    encounter = EncounterFactory()
    result = generate_encounter_description(user, encounter)
    assert result == "Goblins ambush the party."
    mock_claude.assert_called_once()


@patch("ai.adventure.anthropic.Anthropic")
def test_call_claude_wraps_api_error(mock_anthropic_class: MagicMock) -> None:
    import anthropic as anthropic_lib

    mock_client = MagicMock()
    mock_anthropic_class.return_value = mock_client
    mock_client.messages.create.side_effect = anthropic_lib.APIConnectionError(
        request=MagicMock()
    )
    with pytest.raises(AIGenerationError):
        _call_claude("sk-ant-test", "system prompt", "user prompt")
