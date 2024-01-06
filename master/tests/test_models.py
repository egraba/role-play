import pytest

from master.models import Campaign

from .factories import CampaignFactory


@pytest.mark.django_db
class TestCampaignModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.campaign = CampaignFactory(title="campaign")

    def test_creation(self):
        assert isinstance(self.campaign, Campaign)

    def test_str(self):
        assert str(self.campaign) == self.campaign.title
