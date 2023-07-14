from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

import master.forms as mforms
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


class StoryCreateViewTest(TestCase):
    path_name = "story-create"

    @classmethod
    def setUpTestData(cls):
        utusers.create_user()
        mmodels.Story.objects.create(title=utrandom.ascii_letters_string(10))

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(
            response.resolver_match.func.view_class, mviews.StoryCreateView
        )

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertTemplateUsed(response, "master/story_create.html")

    def test_story_creation(self):
        title = utrandom.ascii_letters_string(10)
        synopsis = utrandom.printable_string(800)
        main_conflict = utrandom.printable_string(800)
        objective = utrandom.printable_string(400)
        data = {
            "title": f"{title}",
            "synopsis": f"{synopsis}",
            "main_conflict": f"{main_conflict}",
            "objective": f"{objective}",
        }
        form = mforms.StoryCreateForm(data)
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        story = mmodels.Story.objects.last()
        self.assertRedirects(response, story.get_absolute_url())
        self.assertEqual(story.title, form.cleaned_data["title"])
        self.assertEqual(story.synopsis, form.cleaned_data["synopsis"])
        self.assertEqual(story.main_conflict, form.cleaned_data["main_conflict"])
        self.assertEqual(story.objective, form.cleaned_data["objective"])


class StoryUpdateViewTest(TestCase):
    path_name = "story-update"

    @classmethod
    def setUpTestData(cls):
        utusers.create_user()
        mmodels.Story.objects.create(title=utrandom.ascii_letters_string(10))

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        story = mmodels.Story.objects.last()
        response = self.client.get(reverse(self.path_name, args=(story.slug,)))
        self.assertEqual(
            response.resolver_match.func.view_class, mviews.StoryUpdateView
        )

    def test_template_mapping(self):
        story = mmodels.Story.objects.last()
        response = self.client.get(reverse(self.path_name, args=(story.slug,)))
        self.assertTemplateUsed(response, "master/story_update.html")

    def test_story_update(self):
        synopsis = utrandom.printable_string(800)
        main_conflict = utrandom.printable_string(800)
        objective = utrandom.printable_string(400)
        data = {
            "synopsis": f"{synopsis}",
            "main_conflict": f"{main_conflict}",
            "objective": f"{objective}",
        }
        form = mforms.StoryUpdateForm(data)
        self.assertTrue(form.is_valid())

        story = mmodels.Story.objects.last()
        response = self.client.post(
            reverse(self.path_name, args=(story.slug,)),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, story.get_absolute_url())
        story = mmodels.Story.objects.last()
        self.assertEqual(story.synopsis, form.cleaned_data["synopsis"])
        self.assertEqual(story.main_conflict, form.cleaned_data["main_conflict"])
        self.assertEqual(story.objective, form.cleaned_data["objective"])
