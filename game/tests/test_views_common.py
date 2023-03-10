import random
from datetime import datetime

from django.http import Http404
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from game.models import Character, Event, Game, PendingAction, Tale
from game.tests import utils
from game.views.common import DetailCharacterView, GameView, IndexView


class IndexViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_games = 12
        for i in range(number_of_games):
            Game.objects.create(
                name=utils.generate_random_string(20),
                start_date=datetime.now(tz=timezone.utc),
            )

    def test_view_mapping(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, IndexView)

    def test_template_mapping(self):
        response = self.client.get(reverse("index"))
        self.assertTemplateUsed(response, "game/index.html")

    def test_pagination_size(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["game_list"]), 10)

    def test_pagination_size_next_page(self):
        response = self.client.get(reverse("index") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["game_list"]), 2)

    def test_ordering(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        last_date = 0
        for game in response.context["game_list"]:
            if last_date == 0:
                last_date = game.start_date
            else:
                self.assertTrue(last_date >= game.start_date)
                last_date = game.start_date


class GameViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create(name="game1")
        number_of_events = 22
        for i in range(number_of_events):
            Event.objects.create(
                game=game,
                message=f"{game.name} event{i}",
            )
        number_of_tales = 3
        for i in range(number_of_tales):
            Tale.objects.create(
                game=game,
                description=f"{game.name} tail{i}",
            )
        number_of_characters = 2
        for i in range(number_of_characters):
            character = Character.objects.create(
                game=game,
                name=f"{game.name} character{i}",
                race=random.choice(Character.RACES)[0],
            )
            PendingAction.objects.create(
                game=game,
                character=character,
                action_type=random.choice(PendingAction.ACTION_TYPES)[0],
                message=f"{game.name} pending_action{i}",
            )

    def test_view_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.resolver_match.func.view_class, GameView)

    def test_template_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertTemplateUsed(response, "game/game.html")

    def test_pagination_size(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["event_list"]), 20)

    def test_pagination_size_next_page(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]) + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["event_list"]), 7)  # Inherited events

    def test_ordering_character_name_ascending(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        last_name = ""
        for character in response.context["character_list"]:
            if last_name == "":
                last_name = character.name
            else:
                self.assertTrue(last_name <= character.name)
                last_name = character.name

    def test_ordering_event_date_descending(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        last_date = 0
        for event in response.context["event_list"]:
            if last_date == 0:
                last_date = event.date
            else:
                self.assertTrue(last_date >= event.date)
                last_date = event.date

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse("game", args=[game_id]))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_game_last_tale(self):
        game = Game.objects.last()
        tale = Tale.objects.create(game=game)
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tale"], tale)

    def test_context_data(self):
        for i in range(10):
            game = Game.objects.create(name=f"other_game{i}")
            Tale.objects.create(game=game)
            character = Character.objects.create(game=game, name=f"character{i}")
            Event.objects.create(game=game)
            PendingAction.objects.create(game=game, character=character)
        """
        We test that none of the objects created above are present in the context of
        the game created in setUpTestData().
        """
        game = Game.objects.filter(name="game1").last()
        response = self.client.get(reverse("game", args=[game.id]))
        tale_list = Tale.objects.filter(game__name="game1")
        tale = tale_list.last()
        self.assertEqual(response.context["tale"], tale)
        character_list = Character.objects.filter(game__name="game1")
        self.assertQuerysetEqual(
            list(response.context["character_list"]), character_list
        )
        pending_action_list = PendingAction.objects.filter(game__name="game1")
        self.assertQuerysetEqual(
            list(response.context["pending_action_list"]), pending_action_list
        )
        event_list = Event.objects.filter(game__name="game1")
        self.assertTrue(
            set(response.context["event_list"]).issubset(set(event_list))
        )  # issubset() is used because of pagination.


class CharacterViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Character.objects.create()

    def test_view_mapping(self):
        character = Character.objects.last()
        response = self.client.get(reverse("character-detail", args=[character.id]))
        self.assertEqual(response.resolver_match.func.view_class, DetailCharacterView)

    def test_template_mapping(self):
        character = Character.objects.last()
        response = self.client.get(reverse("character-detail", args=[character.id]))
        self.assertTemplateUsed(response, "game/character.html")
