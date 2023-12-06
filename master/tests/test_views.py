import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from pytest_django.asserts import assertTemplateUsed

from master.forms import CampaignCreateForm, CampaignUpdateForm
from master.models import Campaign
from master.views import (
    CampaignCreateView,
    CampaignDetailView,
    CampaignListView,
    CampaignUpdateView,
)
from utils.testing.factories import CampaignFactory, UserFactory


@pytest.mark.django_db
class TestCampaignDetailView:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        user = UserFactory(username="user")
        client.force_login(user)
        self.campaign = CampaignFactory()

    def test_view_mapping(self, client):
        response = client.get(self.campaign.get_absolute_url())
        assert response.resolver_match.func.view_class == CampaignDetailView

    def test_template_mapping(self, client):
        response = client.get(self.campaign.get_absolute_url())
        assertTemplateUsed(response, "master/campaign.html")


class CampaignListViewTest(TestCase):
    path_name = "campaign-list"

    @classmethod
    def setUpTestData(cls):
        UserFactory()
        number_of_stories = 22
        for i in range(number_of_stories):
            CampaignFactory()

    def setUp(self):
        self.user = User.objects.last()
        self.client.force_login(self.user)

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.resolver_match.func.view_class, CampaignListView)

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertTemplateUsed(response, "master/campaign_list.html")

    def test_pagination_size(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["campaign_list"]), 20)

    def test_pagination_size_next_page(self):
        response = self.client.get(reverse(self.path_name) + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["campaign_list"]), 2)

    def test_ordering(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        title = ""
        for campaign in response.context["campaign_list"]:
            if title == "":
                title = campaign.title.upper()
            else:
                self.assertTrue(title <= campaign.title)
                title = campaign.title.upper()

    def test_content_no_campaign(self):
        Campaign.objects.all().delete()
        response = self.client.get(reverse(self.path_name))
        self.assertContains(response, "There is no campaign available...")


class CampaignCreateViewTest(TestCase):
    path_name = "campaign-create"

    @classmethod
    def setUpTestData(cls):
        UserFactory()
        CampaignFactory()

    def setUp(self):
        self.user = User.objects.last()
        self.client.force_login(self.user)

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.resolver_match.func.view_class, CampaignCreateView)

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertTemplateUsed(response, "master/campaign_create.html")

    def test_campaign_creation(self):
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
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        campaign = Campaign.objects.last()
        self.assertRedirects(response, campaign.get_absolute_url())
        self.assertEqual(campaign.title, form.cleaned_data["title"])
        self.assertEqual(campaign.synopsis, form.cleaned_data["synopsis"])
        self.assertEqual(campaign.main_conflict, form.cleaned_data["main_conflict"])
        self.assertEqual(campaign.objective, form.cleaned_data["objective"])


class CampaignUpdateViewTest(TestCase):
    path_name = "campaign-update"

    @classmethod
    def setUpTestData(cls):
        UserFactory()
        CampaignFactory()

    def setUp(self):
        self.user = User.objects.last()
        self.client.force_login(self.user)

    def test_view_mapping(self):
        campaign = Campaign.objects.last()
        response = self.client.get(reverse(self.path_name, args=(campaign.slug,)))
        self.assertEqual(response.resolver_match.func.view_class, CampaignUpdateView)

    def test_template_mapping(self):
        campaign = Campaign.objects.last()
        response = self.client.get(reverse(self.path_name, args=(campaign.slug,)))
        self.assertTemplateUsed(response, "master/campaign_update.html")

    def test_campaign_update(self):
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
        self.assertTrue(form.is_valid())

        campaign = Campaign.objects.last()
        response = self.client.post(
            reverse(self.path_name, args=(campaign.slug,)),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, campaign.get_absolute_url())
        campaign = Campaign.objects.last()
        self.assertEqual(campaign.synopsis, form.cleaned_data["synopsis"])
        self.assertEqual(campaign.main_conflict, form.cleaned_data["main_conflict"])
        self.assertEqual(campaign.objective, form.cleaned_data["objective"])
