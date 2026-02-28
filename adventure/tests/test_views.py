import pytest
from django.urls import reverse

from adventure.models import Campaign
from adventure.tests.factories import CampaignFactory
from user.tests.factories import UserFactory


@pytest.mark.django_db
def test_campaign_list_requires_login(client):
    response = client.get(reverse("adventure:campaign-list"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_campaign_list_shows_own_campaigns(client):
    user = UserFactory()
    campaign = CampaignFactory(owner=user)
    other = CampaignFactory()  # different owner
    client.force_login(user)
    response = client.get(reverse("adventure:campaign-list"))
    assert response.status_code == 200
    assert campaign.title in response.content.decode()
    assert other.title not in response.content.decode()


@pytest.mark.django_db
def test_campaign_detail_accessible_by_owner(client):
    user = UserFactory()
    campaign = CampaignFactory(owner=user)
    client.force_login(user)
    response = client.get(
        reverse("adventure:campaign-detail", kwargs={"slug": campaign.slug})
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_campaign_detail_inaccessible_by_non_owner(client):
    user = UserFactory()
    campaign = CampaignFactory()  # different owner
    client.force_login(user)
    response = client.get(
        reverse("adventure:campaign-detail", kwargs={"slug": campaign.slug})
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_campaign_create(client):
    user = UserFactory()
    client.force_login(user)
    response = client.post(
        reverse("adventure:campaign-create"),
        {
            "title": "Test Campaign",
            "synopsis": "A test",
            "main_conflict": "",
            "objective": "",
            "party_level": 1,
            "tone": "heroic",
            "setting": "",
        },
    )
    assert response.status_code == 302
    assert Campaign.objects.filter(title="Test Campaign", owner=user).exists()


@pytest.mark.django_db
def test_campaign_delete(client):
    user = UserFactory()
    campaign = CampaignFactory(owner=user)
    client.force_login(user)
    response = client.post(
        reverse("adventure:campaign-delete", kwargs={"slug": campaign.slug})
    )
    assert response.status_code == 302
    assert not Campaign.objects.filter(pk=campaign.pk).exists()
