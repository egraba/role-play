import pytest

from adventure.tests.factories import CampaignFactory


@pytest.mark.django_db
def test_adventure_campaign_can_be_created_independently_of_master():
    """Verify adventure.Campaign is a standalone model, not dependent on master."""
    campaign = CampaignFactory(title="Standalone Adventure")
    assert campaign.pk is not None
    assert campaign.owner is not None
