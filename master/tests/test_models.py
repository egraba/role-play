from django.db import models
from django.test import TestCase

import master.models as mmodels


class StoryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        mmodels.Story.objects.create()

    def test_name_type(self):
        story = mmodels.Story.objects.last()
        name = story._meta.get_field("name")
        self.assertTrue(name, models.CharField)

    def test_name_max_length(self):
        story = mmodels.Story.objects.last()
        max_length = story._meta.get_field("name").max_length
        self.assertEqual(max_length, 50)
