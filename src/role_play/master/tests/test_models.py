import pytest

from master.models import Campaign

from .factories import CampaignFactory


@pytest.mark.django_db
class TestCampaignModel:
    @pytest.fixture
    def campaign(self):
        return CampaignFactory(title="campaign")

    def test_creation(self, campaign):
        assert isinstance(campaign, Campaign)

    def test_str(self, campaign):
        assert str(campaign) == campaign.title
