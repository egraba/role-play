"""Tests for AI HTMX draft endpoints."""

from unittest.mock import patch

import pytest
from django.urls import reverse

from adventure.exceptions import AIGenerationError
from adventure.tests.factories import (
    ActFactory,
    CampaignFactory,
    EncounterFactory,
    LocationFactory,
    NPCFactory,
    SceneFactory,
)
from user.tests.factories import UserFactory


# ---------------------------------------------------------------------------
# Campaign synopsis
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_ai_draft_synopsis_requires_login(client):
    campaign = CampaignFactory()
    response = client.post(
        reverse("adventure:ai-draft-campaign-synopsis", kwargs={"slug": campaign.slug})
    )
    assert response.status_code == 302  # redirect to login


@pytest.mark.django_db
@patch("adventure.views.generate_campaign_synopsis")
def test_ai_draft_synopsis_returns_html(mock_generate, client):
    mock_generate.return_value = "A great campaign synopsis."
    user = UserFactory(anthropic_api_key="sk-ant-test")
    campaign = CampaignFactory(owner=user)
    client.force_login(user)
    response = client.post(
        reverse("adventure:ai-draft-campaign-synopsis", kwargs={"slug": campaign.slug})
    )
    assert response.status_code == 200
    assert b"A great campaign synopsis." in response.content
    assert b"<textarea" in response.content
    assert b'name="synopsis"' in response.content


@pytest.mark.django_db
@patch("adventure.views.generate_campaign_synopsis")
def test_ai_draft_synopsis_returns_error_on_failure(mock_generate, client):
    mock_generate.side_effect = AIGenerationError("No API key configured.")
    user = UserFactory()
    campaign = CampaignFactory(owner=user)
    client.force_login(user)
    response = client.post(
        reverse("adventure:ai-draft-campaign-synopsis", kwargs={"slug": campaign.slug})
    )
    assert response.status_code == 200
    assert b"No API key configured." in response.content


@pytest.mark.django_db
def test_ai_draft_synopsis_non_owner_gets_404(client):
    user = UserFactory()
    campaign = CampaignFactory()  # different owner
    client.force_login(user)
    response = client.post(
        reverse("adventure:ai-draft-campaign-synopsis", kwargs={"slug": campaign.slug})
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Act summary
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_ai_draft_act_summary_requires_login(client):
    act = ActFactory()
    response = client.post(
        reverse(
            "adventure:ai-draft-act-summary",
            kwargs={"slug": act.campaign.slug, "pk": act.pk},
        )
    )
    assert response.status_code == 302


@pytest.mark.django_db
@patch("adventure.views.generate_act_summary")
def test_ai_draft_act_summary_returns_html(mock_generate, client):
    mock_generate.return_value = "Act summary text."
    user = UserFactory()
    campaign = CampaignFactory(owner=user)
    act = ActFactory(campaign=campaign)
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:ai-draft-act-summary",
            kwargs={"slug": campaign.slug, "pk": act.pk},
        )
    )
    assert response.status_code == 200
    assert b"Act summary text." in response.content
    assert b"<textarea" in response.content
    assert b'name="summary"' in response.content


@pytest.mark.django_db
@patch("adventure.views.generate_act_summary")
def test_ai_draft_act_summary_returns_error_on_failure(mock_generate, client):
    mock_generate.side_effect = AIGenerationError("API error.")
    user = UserFactory()
    campaign = CampaignFactory(owner=user)
    act = ActFactory(campaign=campaign)
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:ai-draft-act-summary",
            kwargs={"slug": campaign.slug, "pk": act.pk},
        )
    )
    assert response.status_code == 200
    assert b"API error." in response.content


@pytest.mark.django_db
def test_ai_draft_act_summary_non_owner_gets_404(client):
    user = UserFactory()
    act = ActFactory()  # different owner
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:ai-draft-act-summary",
            kwargs={"slug": act.campaign.slug, "pk": act.pk},
        )
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Scene description
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_ai_draft_scene_description_requires_login(client):
    scene = SceneFactory()
    act = scene.act
    response = client.post(
        reverse(
            "adventure:ai-draft-scene-description",
            kwargs={
                "slug": act.campaign.slug,
                "act_pk": act.pk,
                "pk": scene.pk,
            },
        )
    )
    assert response.status_code == 302


@pytest.mark.django_db
@patch("adventure.views.generate_scene_description")
def test_ai_draft_scene_description_returns_html(mock_generate, client):
    mock_generate.return_value = "Scene description text."
    user = UserFactory()
    campaign = CampaignFactory(owner=user)
    act = ActFactory(campaign=campaign)
    scene = SceneFactory(act=act)
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:ai-draft-scene-description",
            kwargs={"slug": campaign.slug, "act_pk": act.pk, "pk": scene.pk},
        )
    )
    assert response.status_code == 200
    assert b"Scene description text." in response.content
    assert b"<textarea" in response.content
    assert b'name="description"' in response.content


@pytest.mark.django_db
def test_ai_draft_scene_description_non_owner_gets_404(client):
    user = UserFactory()
    scene = SceneFactory()
    act = scene.act
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:ai-draft-scene-description",
            kwargs={
                "slug": act.campaign.slug,
                "act_pk": act.pk,
                "pk": scene.pk,
            },
        )
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# NPC personality
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_ai_draft_npc_personality_requires_login(client):
    npc = NPCFactory()
    response = client.post(
        reverse(
            "adventure:ai-draft-npc-personality",
            kwargs={"slug": npc.campaign.slug, "pk": npc.pk},
        )
    )
    assert response.status_code == 302


@pytest.mark.django_db
@patch("adventure.views.generate_npc_personality")
def test_ai_draft_npc_personality_returns_html(mock_generate, client):
    mock_generate.return_value = "NPC personality text."
    user = UserFactory()
    campaign = CampaignFactory(owner=user)
    npc = NPCFactory(campaign=campaign)
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:ai-draft-npc-personality",
            kwargs={"slug": campaign.slug, "pk": npc.pk},
        )
    )
    assert response.status_code == 200
    assert b"NPC personality text." in response.content
    assert b"<textarea" in response.content
    assert b'name="personality"' in response.content


@pytest.mark.django_db
def test_ai_draft_npc_personality_non_owner_gets_404(client):
    user = UserFactory()
    npc = NPCFactory()
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:ai-draft-npc-personality",
            kwargs={"slug": npc.campaign.slug, "pk": npc.pk},
        )
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Location description
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_ai_draft_location_description_requires_login(client):
    location = LocationFactory()
    response = client.post(
        reverse(
            "adventure:ai-draft-location-description",
            kwargs={"slug": location.campaign.slug, "pk": location.pk},
        )
    )
    assert response.status_code == 302


@pytest.mark.django_db
@patch("adventure.views.generate_location_description")
def test_ai_draft_location_description_returns_html(mock_generate, client):
    mock_generate.return_value = "Location description text."
    user = UserFactory()
    campaign = CampaignFactory(owner=user)
    location = LocationFactory(campaign=campaign)
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:ai-draft-location-description",
            kwargs={"slug": campaign.slug, "pk": location.pk},
        )
    )
    assert response.status_code == 200
    assert b"Location description text." in response.content
    assert b"<textarea" in response.content
    assert b'name="description"' in response.content


@pytest.mark.django_db
def test_ai_draft_location_description_non_owner_gets_404(client):
    user = UserFactory()
    location = LocationFactory()
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:ai-draft-location-description",
            kwargs={"slug": location.campaign.slug, "pk": location.pk},
        )
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Encounter description
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_ai_draft_encounter_description_requires_login(client):
    encounter = EncounterFactory()
    scene = encounter.scene
    act = scene.act
    response = client.post(
        reverse(
            "adventure:ai-draft-encounter-description",
            kwargs={
                "slug": act.campaign.slug,
                "act_pk": act.pk,
                "scene_pk": scene.pk,
                "pk": encounter.pk,
            },
        )
    )
    assert response.status_code == 302


@pytest.mark.django_db
@patch("adventure.views.generate_encounter_description")
def test_ai_draft_encounter_description_returns_html(mock_generate, client):
    mock_generate.return_value = "Encounter description text."
    user = UserFactory()
    campaign = CampaignFactory(owner=user)
    act = ActFactory(campaign=campaign)
    scene = SceneFactory(act=act)
    encounter = EncounterFactory(scene=scene)
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:ai-draft-encounter-description",
            kwargs={
                "slug": campaign.slug,
                "act_pk": act.pk,
                "scene_pk": scene.pk,
                "pk": encounter.pk,
            },
        )
    )
    assert response.status_code == 200
    assert b"Encounter description text." in response.content
    assert b"<textarea" in response.content
    assert b'name="description"' in response.content


@pytest.mark.django_db
def test_ai_draft_encounter_description_non_owner_gets_404(client):
    user = UserFactory()
    encounter = EncounterFactory()
    scene = encounter.scene
    act = scene.act
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:ai-draft-encounter-description",
            kwargs={
                "slug": act.campaign.slug,
                "act_pk": act.pk,
                "scene_pk": scene.pk,
                "pk": encounter.pk,
            },
        )
    )
    assert response.status_code == 404
