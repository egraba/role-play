import random
from datetime import datetime, timezone

from django.contrib.auth.models import Permission, User
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.test import TestCase
from django.urls import reverse

import game.models as gmodels
import game.views.common as gvcommon
from game.tests import utils


class IndexViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="add_game")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()

        number_of_games = 10
        for i in range(number_of_games):
            game = gmodels.Game.objects.create(
                name=utils.generate_random_string(20),
                start_date=datetime.now(tz=timezone.utc),
            )
            if i < (number_of_games - 3):
                game.user = user
                game.save()

    def test_view_mapping(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, gvcommon.IndexView)

    def test_template_mapping(self):
        response = self.client.get(reverse("index"))
        self.assertTemplateUsed(response, "game/index.html")

    def test_pagination_size(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["game_list"]), 5)

    def test_pagination_size_next_page(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

        response = self.client.get(reverse("index") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["game_list"]), 2)

    def test_ordering(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        last_date = 0
        for game in response.context["game_list"]:
            if last_date == 0:
                last_date = game.start_date
            else:
                self.assertTrue(last_date >= game.start_date)
                last_date = game.start_date

    def test_context_data_master_logged(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        game_list = gmodels.Game.objects.filter(user=self.user)
        self.assertTrue(set(response.context["game_list"]).issubset(set(game_list)))

    def test_context_data_anonymous_user(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["game_list"].exists())

    def test_context_data_player_logged(self):
        permission = Permission.objects.get(codename="add_character")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()
        self.client.login(username=user.username, password="pwd")

        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        game_list = gmodels.Game.objects.filter(character__user=user)
        self.assertQuerysetEqual(response.context["game_list"], game_list)

    def test_context_data_player_logged_no_existing_character(self):
        permission = Permission.objects.get(codename="add_character")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()
        self.client.login(username=user.username, password="pwd")

        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(KeyError):
            response.context["pending_action"]
        self.assertRaises(ObjectDoesNotExist)

    def test_context_data_player_logged_existing_character(self):
        permission = Permission.objects.get(codename="add_character")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()

        gmodels.Character.objects.create(name=utils.generate_random_name(5), user=user)
        self.client.login(username=user.username, password="pwd")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        character = gmodels.Character.objects.last()
        self.assertEqual(response.context["character"], character)


class GameViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.save()

        game = gmodels.Game.objects.create(name="game1")
        number_of_events = 22
        for i in range(number_of_events):
            gmodels.Event.objects.create(
                game=game,
                message=f"{game.name} event{i}",
            )
        number_of_tales = 3
        for i in range(number_of_tales):
            gmodels.Tale.objects.create(
                game=game,
                description=f"{game.name} tail{i}",
            )
        number_of_characters = 2
        for i in range(number_of_characters):
            character = gmodels.Character.objects.create(
                game=game,
                name=f"{game.name} character{i}",
                race=random.choice(gmodels.Character.RACES)[0],
            )
            gmodels.PendingAction.objects.create(
                game=game,
                character=character,
                action_type=random.choice(gmodels.PendingAction.ACTION_TYPES)[0],
                message=f"{game.name} pending_action{i}",
            )

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = gmodels.Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.resolver_match.func.view_class, gvcommon.GameView)

    def test_template_mapping(self):
        game = gmodels.Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertTemplateUsed(response, "game/game.html")

    def test_pagination_size(self):
        game = gmodels.Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["event_list"]), 20)

    def test_pagination_size_next_page(self):
        game = gmodels.Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]) + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["event_list"]), 7)  # Inherited events

    def test_ordering_character_name_ascending(self):
        game = gmodels.Game.objects.last()
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
        game = gmodels.Game.objects.last()
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
        game = gmodels.Game.objects.last()
        tale = gmodels.Tale.objects.create(game=game)
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tale"], tale)

    def test_context_data_master(self):
        number_of_games = 3
        for i in range(number_of_games):
            game = gmodels.Game.objects.create(name=f"other_game{i}")
            gmodels.Tale.objects.create(game=game)
            character = gmodels.Character.objects.create(
                game=game, name=f"character{i}"
            )
            gmodels.Event.objects.create(game=game)
            gmodels.PendingAction.objects.create(game=game, character=character)

        game = gmodels.Game.objects.filter(name="game1").last()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)

        tale_list = gmodels.Tale.objects.filter(game__name="game1")
        tale = tale_list.last()
        self.assertEqual(response.context["tale"], tale)
        character_list = gmodels.Character.objects.filter(game__name="game1")
        self.assertQuerysetEqual(
            list(response.context["character_list"]), character_list
        )
        event_list = gmodels.Event.objects.filter(game__name="game1")
        self.assertTrue(
            set(response.context["event_list"]).issubset(set(event_list))
        )  # issubset() is used because of pagination.
        with self.assertRaises(KeyError):
            response.context["player"]
        with self.assertRaises(KeyError):
            response.context["pending_action"]

    def test_context_data_player(self):
        number_of_games = 3
        for i in range(number_of_games):
            game = gmodels.Game.objects.create(name=f"other_game{i}")
            gmodels.Tale.objects.create(game=game)
            character = gmodels.Character.objects.create(
                game=game, name=f"character{i}"
            )
            gmodels.Event.objects.create(game=game)
            gmodels.PendingAction.objects.create(game=game, character=character)

        player = gmodels.Character.objects.filter(name="game1 character1").get()
        player.user = self.user
        player.save()
        self.client.logout()
        self.client.login(username=self.user.username, password="pwd")

        game = gmodels.Game.objects.filter(name="game1").last()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)

        tale_list = gmodels.Tale.objects.filter(game__name="game1")
        tale = tale_list.last()
        self.assertEqual(response.context["tale"], tale)
        character_list = gmodels.Character.objects.filter(game__name="game1")
        self.assertQuerysetEqual(
            list(response.context["character_list"]), character_list
        )
        event_list = gmodels.Event.objects.filter(game__name="game1")
        self.assertTrue(
            set(response.context["event_list"]).issubset(set(event_list))
        )  # issubset() is used because of pagination.
        self.assertEqual(response.context["player"], player)
        pending_action = gmodels.PendingAction.objects.filter(
            game__name="game1", character__name="game1 character1"
        ).get()
        self.assertEqual(response.context["pending_action"], pending_action)
        gmodels.PendingAction.objects.filter(
            game__name="game1", character__name="game1 character1"
        ).delete()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertRaises(ObjectDoesNotExist)


class CharacterViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        gmodels.Character.objects.create()

    def test_view_mapping(self):
        character = gmodels.Character.objects.last()
        response = self.client.get(reverse("character-detail", args=[character.id]))
        self.assertEqual(
            response.resolver_match.func.view_class, gvcommon.DetailCharacterView
        )

    def test_template_mapping(self):
        character = gmodels.Character.objects.last()
        response = self.client.get(reverse("character-detail", args=[character.id]))
        self.assertTemplateUsed(response, "game/character.html")
