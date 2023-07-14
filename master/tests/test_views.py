from django.contrib.auth.models import User
from django.test import TestCase

import master.models as mmodels
import master.views as mviews
import utils.testing.random as utrandom
import utils.testing.users as utusers


class StoryDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        utusers.create_user()
        mmodels.Story.objects.create(title=utrandom.ascii_letters_string(10))

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        story = mmodels.Story.objects.last()
        response = self.client.get(story.get_absolute_url())
        self.assertEqual(
            response.resolver_match.func.view_class, mviews.StoryDetailView
        )

    def test_template_mapping(self):
        story = mmodels.Story.objects.last()
        response = self.client.get(story.get_absolute_url())
        self.assertTemplateUsed(response, "master/story.html")
