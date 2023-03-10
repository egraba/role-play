import random

from django.contrib.auth.models import Permission, User
from django.http import Http404
from django.test import TestCase
from django.urls import reverse

from game.forms import CreateGameForm, CreateTaleForm
from game.models import Character, Game, Tale
from game.tests import utils
from game.views.master import (
    AddCharacterView,
    CreateGameView,
    CreateTaleView,
    EndGameView,
    StartGameView,
)


class CreateGameViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="add_game")
        user = User.objects.get_or_create(username="Thomas")[0]
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        response = self.client.get(reverse("game-create"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, CreateGameView)

    def test_template_mapping(self):
        response = self.client.get(reverse("game-create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/creategame.html")

    def test_game_creation(self):
        name = utils.generate_random_name(20)
        description = utils.generate_random_string(100)
        data = {"name": f"{name}", "description": f"{description}"}
        form = CreateGameForm(data)
        self.assertTrue(form.is_valid())
        response = self.client.post(reverse("game-create"), data=form.cleaned_data)
        self.assertEqual(response.status_code, 302)
        game = Game.objects.last()
        self.assertEqual(game.name, name)
        tale = Tale.objects.last()
        self.assertEqual(tale.game, game)
        self.assertEqual(tale.message, "The Master created the story.")
        self.assertEqual(tale.description, form.cleaned_data["description"])
        self.assertRedirects(response, reverse("index"))


class AddCharacterViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="change_character")
        user = User.objects.get_or_create(username="Thomas")[0]
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()
        game = Game.objects.create()
        number_of_characters_with_game = 5
        number_of_characters_without_game = 12
        for i in range(number_of_characters_with_game):
            Character.objects.create(
                name=utils.generate_random_name(10),
                game=game,
                race=random.choice(Character.RACES)[0],
            )
        for i in range(number_of_characters_without_game):
            Character.objects.create(
                name=utils.generate_random_name(10),
                race=random.choice(Character.RACES)[0],
            )

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-add-character", args=[game.id]))
        self.assertEqual(response.resolver_match.func.view_class, AddCharacterView)

    def test_template_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-add-character", args=[game.id]))
        self.assertTemplateUsed(response, "game/addcharacter.html")

    def test_pagination_size(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-add-character", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["character_list"]), 10)

    def test_pagination_size_next_page(self):
        game = Game.objects.last()
        response = self.client.get(
            reverse("game-add-character", args=[game.id]) + "?page=2"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["character_list"]), 2)

    def test_ordering(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-add-character", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        last_xp = 0
        for character in response.context["character_list"]:
            if last_xp == 0:
                last_xp = character.xp
            else:
                self.assertTrue(last_xp >= character.xp)
                last_xp = character.xp

    def test_game_exists(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-add-character", args=[game.id]))
        self.assertEqual(response.status_code, 200)

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse("game-add-character", args=[game_id]))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)


class StartGameViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="change_game")
        user = User.objects.get_or_create(username="Thomas")[0]
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()
        Game.objects.create()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-start", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, StartGameView)

    def test_template_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-start", args=[game.id]))
        self.assertTemplateUsed(response, "game/startgame.html")


class EndGameViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="change_game")
        user = User.objects.get_or_create(username="Thomas")[0]
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()
        Game.objects.create()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-end", args=[game.id]))
        self.assertEqual(response.resolver_match.func.view_class, EndGameView)

    def test_template_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-end", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/endgame.html")


class CreateTaleViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="add_tale")
        user = User.objects.get_or_create(username="Thomas")[0]
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()
        Game.objects.create()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("tale-create", args=[game.id]))
        self.assertEqual(response.resolver_match.func.view_class, CreateTaleView)

    def test_template_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("tale-create", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/createtale.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse("tale-create", args=[game_id]))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_context_data(self):
        game = Game.objects.last()
        response = self.client.get(reverse("tale-create", args=[game.id]))
        self.assertEquals(response.context["game"], game)

    def test_tale_creation(self):
        description = utils.generate_random_string(100)
        data = {"description": f"{description}"}
        form = CreateTaleForm(data)
        self.assertTrue(form.is_valid())
        game = Game.objects.last()
        response = self.client.post(
            reverse("tale-create", args=[game.id]), data=form.cleaned_data
        )
        self.assertEqual(response.status_code, 302)
        tale = Tale.objects.last()
        self.assertEqual(tale.game, game)
        self.assertEqual(tale.message, "The Master updated the story.")
        self.assertEqual(tale.description, form.cleaned_data["description"])
        self.assertRedirects(response, reverse("game", args=[game.id]))
