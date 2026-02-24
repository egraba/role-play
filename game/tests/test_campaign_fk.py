import pytest

from adventure.tests.factories import CampaignFactory
from game.tests.factories import GameFactory


@pytest.mark.django_db
def test_game_campaign_is_adventure_campaign():
    campaign = CampaignFactory()
    game = GameFactory(campaign=campaign)
    game.refresh_from_db()
    assert game.campaign == campaign
    assert game.campaign.__class__.__name__ == "Campaign"
    assert game.campaign.__class__.__module__.startswith("adventure")
