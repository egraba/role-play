import pytest
from django.urls import reverse
from faker import Faker
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from master.forms import CampaignCreateForm, CampaignUpdateForm
from master.models import Campaign
from master.views import (
    CampaignCreateView,
    CampaignDetailView,
    CampaignListView,
    CampaignUpdateView,
)
from utils.factories import UserFactory

from .factories import CampaignFactory


@pytest.fixture(scope="class")
def create_campaigns(django_db_blocker):
    with django_db_blocker.unblock():
        Campaign.objects.all().delete()
        number_of_campaigns = 22
        for _ in range(number_of_campaigns):
            CampaignFactory()


@pytest.mark.django_db
class TestCampaignDetailView:
    @pytest.fixture(autouse=True)
    def login(self, client):
        user = UserFactory(username="user")
        client.force_login(user)

    @pytest.fixture
    def campaign(self):
        return CampaignFactory()

    def test_view_mapping(self, client, campaign):
        response = client.get(campaign.get_absolute_url())
        assert response.resolver_match.func.view_class == CampaignDetailView

    def test_template_mapping(self, client, campaign):
        response = client.get(campaign.get_absolute_url())
        assertTemplateUsed(response, "master/campaign.html")


@pytest.mark.django_db
class TestCampaignListView:
    path_name = "campaign-list"

    @pytest.fixture(autouse=True)
    def login(self, client):
        user = UserFactory(username="user")
        client.force_login(user)

    def test_view_mapping(self, client):
        response = client.get(reverse(self.path_name))
        assert response.resolver_match.func.view_class == CampaignListView

    def test_template_mapping(self, client):
        response = client.get(reverse(self.path_name))
        assertTemplateUsed(response, "master/campaign_list.html")

    def test_pagination_size(self, client, create_campaigns):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["campaign_list"]) == 20

    def test_pagination_size_next_page(self, client, create_campaigns):
        response = client.get(reverse(self.path_name) + "?page=2")
        assert response.status_code == 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["campaign_list"]) == 2

    def test_ordering(self, client, create_campaigns):
        response = client.get(reverse(self.path_name))
        assert response.status_code, 200
        title = ""
        for campaign in response.context["campaign_list"]:
            if title == "":
                title = campaign.title.upper()
            else:
                assert title <= campaign.title
                title = campaign.title.upper()

    def test_content_no_campaign(self, client):
        Campaign.objects.all().delete()
        response = client.get(reverse(self.path_name))
        assertContains(response, "There is no campaign available...")


@pytest.mark.django_db
class TestCampaignCreateView:
    path_name = "campaign-create"

    @pytest.fixture(autouse=True)
    def setup(self, client):
        user = UserFactory(username="user")
        client.force_login(user)

    def test_view_mapping(self, client):
        response = client.get(reverse(self.path_name))
        assert response.resolver_match.func.view_class == CampaignCreateView

    def test_template_mapping(self, client):
        response = client.get(reverse(self.path_name))
        assertTemplateUsed(response, "master/campaign_create.html")

    def test_campaign_creation(self, client):
        fake = Faker()
        title = fake.text(max_nb_chars=10)
        synopsis = fake.text(max_nb_chars=900)
        main_conflict = fake.text(max_nb_chars=800)
        objective = fake.text(max_nb_chars=400)
        data = {
            "title": f"{title}",
            "synopsis": f"{synopsis}",
            "main_conflict": f"{main_conflict}",
            "objective": f"{objective}",
        }
        form = CampaignCreateForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        campaign = Campaign.objects.last()
        assertRedirects(response, campaign.get_absolute_url())
        assert campaign.title == form.cleaned_data["title"]
        assert campaign.synopsis == form.cleaned_data["synopsis"]
        assert campaign.main_conflict == form.cleaned_data["main_conflict"]
        assert campaign.objective == form.cleaned_data["objective"]


@pytest.mark.django_db
class TestCampaignUpdateView:
    path_name = "campaign-update"

    @pytest.fixture(autouse=True)
    def login(self, client):
        user = UserFactory(username="user")
        client.force_login(user)

    @pytest.fixture
    def campaign(self):
        return CampaignFactory(title="campaign")

    def test_view_mapping(self, client, campaign):
        response = client.get(reverse(self.path_name, args=(campaign.slug,)))
        assert response.resolver_match.func.view_class == CampaignUpdateView

    def test_template_mapping(self, client, campaign):
        response = client.get(reverse(self.path_name, args=(campaign.slug,)))
        assertTemplateUsed(response, "master/campaign_update.html")

    def test_campaign_update(self, client, campaign):
        fake = Faker()
        synopsis = fake.text(max_nb_chars=900)
        main_conflict = fake.text(max_nb_chars=800)
        objective = fake.text(max_nb_chars=400)
        data = {
            "synopsis": f"{synopsis}",
            "main_conflict": f"{main_conflict}",
            "objective": f"{objective}",
        }
        form = CampaignUpdateForm(data)
        assert form.is_valid()

        campaign = Campaign.objects.last()
        response = client.post(
            reverse(self.path_name, args=(campaign.slug,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, campaign.get_absolute_url())
        campaign = Campaign.objects.last()
        assert campaign.synopsis == form.cleaned_data["synopsis"]
        assert campaign.main_conflict == form.cleaned_data["main_conflict"]
        assert campaign.objective == form.cleaned_data["objective"]
