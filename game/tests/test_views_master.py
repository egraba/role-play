import random

from django.http import Http404
from django.test import TestCase
from django.urls import reverse

from game.forms import CreateGameForm
from game.models import Character, Game, Tale
from game.tests import utils
from game.views.master import (
    AddCharacterView,
    CreateGameView,
    EndGameView,
    StartGameView,
)


class CreateGameViewTest(TestCase):
    def test_view_mapping(self):
        response = self.client.get(reverse("game-create"))
        self.assertEqual(response.resolver_match.func.view_class, CreateGameView)

    def test_template_mapping(self):
        response = self.client.get(reverse("game-create"))
        self.assertTemplateUsed(response, "game/creategame.html")

    def test_form_valid(self):
        name = utils.generate_random_name(20)
        description = utils.generate_random_string(100)
        data = {"name": f"{name}", "description": f"{description}"}
        form = CreateGameForm(data)
        self.assertTrue(form.is_valid())
        response = self.client.post(reverse("game-create"), data=form.cleaned_data)
        game = Game.objects.last()
        self.assertEqual(game.name, name)
        tale = Tale.objects.last()
        self.assertEqual(tale.game, game)
        self.assertEqual(tale.message, "The Master created the story.")
        self.assertEqual(tale.description, description)
        self.assertRedirects(response, reverse("index"))


class AddCharacterViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
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

    def test_view_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("add_character", args=[game.id]))
        self.assertEqual(response.resolver_match.func.view_class, AddCharacterView)

    def test_template_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("add_character", args=[game.id]))
        self.assertTemplateUsed(response, "game/addcharacter.html")

    def test_pagination_size(self):
        game = Game.objects.last()
        response = self.client.get(reverse("add_character", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["character_list"]), 10)

    def test_pagination_size_next_page(self):
        game = Game.objects.last()
        response = self.client.get(reverse("add_character", args=[game.id]) + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["character_list"]), 2)

    def test_ordering(self):
        game = Game.objects.last()
        response = self.client.get(reverse("add_character", args=[game.id]))
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
        response = self.client.get(reverse("add_character", args=[game.id]))
        self.assertEqual(response.status_code, 200)

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse("add_character", args=[game_id]))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)


class StartGameViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Game.objects.create()

    def test_view_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-start", args=[game.id]))
        self.assertEqual(response.resolver_match.func.view_class, StartGameView)

    def test_template_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-start", args=[game.id]))
        self.assertTemplateUsed(response, "game/startgame.html")


class EndGameViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Game.objects.create()

    def test_view_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-end", args=[game.id]))
        self.assertEqual(response.resolver_match.func.view_class, EndGameView)

    def test_template_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-end", args=[game.id]))
        self.assertTemplateUsed(response, "game/endgame.html")
