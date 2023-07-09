from django.db import models
from django.test import TestCase

import master.models as mmodels


class StoryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        mmodels.Story.objects.create()

    def test_title_type(self):
        story = mmodels.Story.objects.last()
        title = story._meta.get_field("title")
        self.assertTrue(title, models.CharField)

    def test_title_max_length(self):
        story = mmodels.Story.objects.last()
        max_length = story._meta.get_field("title").max_length
        self.assertEqual(max_length, 50)

    def test_synopsis_type(self):
        story = mmodels.Story.objects.last()
        synopsis = story._meta.get_field("synopsis")
        self.assertTrue(synopsis, models.TextField)

    def test_synopsis_max_length(self):
        story = mmodels.Story.objects.last()
        max_length = story._meta.get_field("synopsis").max_length
        self.assertEqual(max_length, 3000)

    def test_main_conflict_type(self):
        story = mmodels.Story.objects.last()
        main_conflict = story._meta.get_field("main_conflict")
        self.assertTrue(main_conflict, models.TextField)

    def test_main_conflict_max_length(self):
        story = mmodels.Story.objects.last()
        max_length = story._meta.get_field("main_conflict").max_length
        self.assertEqual(max_length, 1000)

    def test_str(self):
        story = mmodels.Story.objects.last()
        self.assertEqual(str(story), story.title)
