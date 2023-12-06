import pytest

from utils.testing.factories import CampaignFactory


@pytest.fixture(scope="class")
def create_campaigns(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        number_of_campaigns = 22
        for i in range(number_of_campaigns):
            CampaignFactory()
