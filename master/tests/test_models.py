from django.db import models
from django.test import TestCase

import master.models as mmodels


class StoryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        mmodels.Story.objects.create()

    def setUp(self):
        self.story = mmodels.Story.objects.last()

    def test_title_type(self):
        title = self.story._meta.get_field("title")
        self.assertTrue(title, models.CharField)

    def test_title_max_length(self):
        max_length = self.story._meta.get_field("title").max_length
        self.assertEqual(max_length, 50)

    def test_slug_type(self):
        slug = self.story._meta.get_field("slug")
        self.assertTrue(slug, models.SlugField)

    def test_slug_max_length(self):
        max_length = self.story._meta.get_field("slug").max_length
        self.assertEqual(max_length, 50)

    def test_synopsis_type(self):
        synopsis = self.story._meta.get_field("synopsis")
        self.assertTrue(synopsis, models.TextField)

    def test_synopsis_max_length(self):
        max_length = self.story._meta.get_field("synopsis").max_length
        self.assertEqual(max_length, 3000)

    def test_main_conflict_type(self):
        main_conflict = self.story._meta.get_field("main_conflict")
        self.assertTrue(main_conflict, models.TextField)

    def test_main_conflict_max_length(self):
        max_length = self.story._meta.get_field("main_conflict").max_length
        self.assertEqual(max_length, 1000)

    def test_objective_type(self):
        objective = self.story._meta.get_field("objective")
        self.assertTrue(objective, models.TextField)

    def test_objective_max_length(self):
        max_length = self.story._meta.get_field("objective").max_length
        self.assertEqual(max_length, 500)

    def test_str(self):
        self.assertEqual(str(self.story), self.story.title)
