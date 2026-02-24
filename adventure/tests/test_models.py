import pytest

from adventure.tests.factories import CampaignFactory


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
    from user.tests.factories import UserFactory

    user = UserFactory()
    campaign = CampaignFactory(owner=user)
    assert campaign.owner == user
