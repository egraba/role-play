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
        Game.objects.create(name=utils.generate_random_string(20))
        game = Game.objects.last()
        number_of_events = 22
        for i in range(number_of_events):
            Event.objects.create(
                game=game,
                message=utils.generate_random_string(100),
            )
        number_of_tales = 3
        for i in range(number_of_tales):
            Tale.objects.create(
                game=game,
                description=utils.generate_random_string(500),
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
        self.assertEqual(len(response.context["event_list"]), 5)

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
        game1 = Game.objects.create()
        tale1 = Tale.objects.create(game=game1, message="tale1")
        character_list1 = list()
        character_list1.append(Character.objects.create(game=game1, name="A"))
        pending_action_list1 = list()
        pending_action_list1.append(
            PendingAction.objects.create(
                game=game1, character=character_list1[0], message="pending_action1"
            )
        )
        event_list1 = list()
        event_list1.append(Event.objects.filter(message="tale1").last())
        event_list1.append(Event.objects.filter(message="pending_action1").last())
        event_list1.append(Event.objects.create(game=game1, message="event1"))

        game2 = Game.objects.create()
        tale2 = Tale.objects.create(game=game2, message="tale2")
        character_list2 = list()
        character_list2.append(Character.objects.create(game=game2, name="B"))
        pending_action_list2 = list()
        pending_action_list2.append(
            PendingAction.objects.create(
                game=game2, character=character_list2[0], message="pending_action2"
            )
        )
        event_list2 = list()
        event_list2.append(Event.objects.filter(message="tale2").last())
        event_list2.append(Event.objects.filter(message="pending_action2").last())
        event_list2.append(Event.objects.create(game=game2, message="event2"))

        """
        We test that game1 contains the context game1 only.
        """
        response = self.client.get(reverse("game", args=[game1.id]))
        self.assertEqual(response.context["tale"], tale1)
        self.assertQuerysetEqual(set(response.context["event_list"]), set(event_list1))
        self.assertQuerysetEqual(
            list(response.context["character_list"]), character_list1
        )
        self.assertQuerysetEqual(
            list(response.context["pending_action_list"]), pending_action_list1
        )

        """
        We test that game2 contains the context game2 only.
        """
        response = self.client.get(reverse("game", args=[game2.id]))
        self.assertEqual(response.context["tale"], tale2)
        self.assertQuerysetEqual(set(response.context["event_list"]), set(event_list2))
        self.assertQuerysetEqual(
            list(response.context["character_list"]), character_list2
        )
        self.assertQuerysetEqual(
            list(response.context["pending_action_list"]), pending_action_list2
        )


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
