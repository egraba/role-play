import random

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

import character.forms as cforms
import character.models as cmodels
import character.views as cviews
import utils.testing.random as utrandom
import utils.testing.users as utusers


class CharacterDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        utusers.create_user()
        cmodels.Character.objects.create()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        character = cmodels.Character.objects.last()
        response = self.client.get(character.get_absolute_url())
        self.assertEqual(
            response.resolver_match.func.view_class, cviews.CharacterDetailView
        )

    def test_template_mapping(self):
        character = cmodels.Character.objects.last()
        response = self.client.get(character.get_absolute_url())
        self.assertTemplateUsed(response, "character/character.html")


class CharacterListViewTest(TestCase):
    path_name = "character-list"

    @classmethod
    def setUpTestData(cls):
        utusers.create_user()
        number_of_characters = 22
        for i in range(number_of_characters):
            user = User.objects.create(username=utrandom.ascii_letters_string(5))
            user.set_password("pwd")
            user.save()
            cmodels.Character.objects.create(
                name=utrandom.ascii_letters_string(20),
                race=random.choice(cmodels.Character.Race.choices)[0],
            )

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, cviews.CharacterListView
        )

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertTemplateUsed(response, "character/character_list.html")

    def test_pagination_size(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["character_list"]), 20)

    def test_pagination_size_next_page(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

        response = self.client.get(reverse(self.path_name) + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["character_list"]), 2)

    def test_ordering(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        xp = 0
        for character in response.context["character_list"]:
            if xp == 0:
                xp = character.xp
            else:
                self.assertTrue(xp >= character.xp)
                xp = character.xp


class CharacterCreateViewTest(TestCase):
    path_name = "character-create"

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username=utrandom.ascii_letters_string(5))
        user.set_password("pwd")
        user.save()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, cviews.CharacterCreateView
        )

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "character/character_create.html")

    def test_character_creation(self):
        name = utrandom.ascii_letters_string(10)
        race = random.choice(cmodels.Character.Race.choices)[0]
        data = {"name": f"{name}", "race": f"{race}"}
        form = cforms.CreateCharacterForm(data)
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        character = cmodels.Character.objects.last()
        self.assertRedirects(response, character.get_absolute_url())
        self.assertEqual(character.name, form.cleaned_data["name"])
        self.assertEqual(character.race, form.cleaned_data["race"])
        self.assertEqual(character.xp, 0)
        self.assertEqual(character.hp, 100)
        self.assertEqual(character.max_hp, 100)
