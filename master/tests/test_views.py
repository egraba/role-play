from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

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


class StoryListViewTest(TestCase):
    path_name = "story-list"

    @classmethod
    def setUpTestData(cls):
        utusers.create_user()
        number_of_stories = 22
        for i in range(number_of_stories):
            mmodels.Story.objects.create(title=utrandom.ascii_letters_string(10))

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.resolver_match.func.view_class, mviews.StoryListView)

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertTemplateUsed(response, "master/story_list.html")

    def test_pagination_size(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["story_list"]), 20)

    def test_pagination_size_next_page(self):
        response = self.client.get(reverse(self.path_name) + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["story_list"]), 2)

    def test_ordering(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        title = ""
        for story in response.context["story_list"]:
            if title == "":
                title = story.title
            else:
                self.assertTrue(title <= story.title)
                title = story.title
