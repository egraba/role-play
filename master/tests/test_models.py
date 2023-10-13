from django.db import models
from django.test import TestCase

from master.models import Campaign


class CampaignModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Campaign.objects.create()

    def setUp(self):
        self.campaign = Campaign.objects.last()

    def test_title_type(self):
        title = self.campaign._meta.get_field("title")
        self.assertTrue(title, models.CharField)

    def test_title_max_length(self):
        max_length = self.campaign._meta.get_field("title").max_length
        self.assertEqual(max_length, 50)

    def test_slug_type(self):
        slug = self.campaign._meta.get_field("slug")
        self.assertTrue(slug, models.SlugField)

    def test_slug_max_length(self):
        max_length = self.campaign._meta.get_field("slug").max_length
        self.assertEqual(max_length, 50)

    def test_synopsis_type(self):
        synopsis = self.campaign._meta.get_field("synopsis")
        self.assertTrue(synopsis, models.TextField)

    def test_synopsis_max_length(self):
        max_length = self.campaign._meta.get_field("synopsis").max_length
        self.assertEqual(max_length, 3000)

    def test_main_conflict_type(self):
        main_conflict = self.campaign._meta.get_field("main_conflict")
        self.assertTrue(main_conflict, models.TextField)

    def test_main_conflict_max_length(self):
        max_length = self.campaign._meta.get_field("main_conflict").max_length
        self.assertEqual(max_length, 1000)

    def test_objective_type(self):
        objective = self.campaign._meta.get_field("objective")
        self.assertTrue(objective, models.TextField)

    def test_objective_max_length(self):
        max_length = self.campaign._meta.get_field("objective").max_length
        self.assertEqual(max_length, 500)

    def test_str(self):
        self.assertEqual(str(self.campaign), self.campaign.title)
