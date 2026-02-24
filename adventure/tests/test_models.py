import pytest

from adventure.tests.factories import CampaignFactory
from user.tests.factories import UserFactory


@pytest.mark.django_db
def test_campaign_str():
    campaign = CampaignFactory(title="The Lost Mine")
    assert str(campaign) == "The Lost Mine"


@pytest.mark.django_db
def test_campaign_slug_auto_generated():
    campaign = CampaignFactory(title="The Lost Mine of Phandelver")
    assert campaign.slug == "the-lost-mine-of-phandelver"


@pytest.mark.django_db
def test_campaign_has_owner():
    user = UserFactory()
    campaign = CampaignFactory(owner=user)
    assert campaign.owner == user


@pytest.mark.django_db
@pytest.mark.skip(reason="URL config registered in Task 9")
def test_campaign_get_absolute_url():
    campaign = CampaignFactory(title="Test Campaign")
    assert campaign.get_absolute_url() == f"/adventure/{campaign.slug}/"
