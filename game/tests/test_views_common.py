import random
from datetime import datetime, timezone

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import TestCase
from django.urls import reverse

import game.forms as gforms
import game.models as gmodels
import game.views.common as gvcommon
import master.models as mmodels
from game.tests import utils


class IndexViewTest(TestCase):
    path_name = "index"

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, gvcommon.IndexView)

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertTemplateUsed(response, "game/index.html")

    def test_content_anonymous_user(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Log in")
        self.assertContains(response, "Register")
        self.assertNotContains(response, "View all games")
        self.assertNotContains(response, "View all characters")
        self.assertNotContains(response, "Create a new game")
        self.assertNotContains(response, "Create a new character")
        self.assertNotContains(response, "View your character")

    def test_content_logged_user_no_character(self):
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.save()
        self.client.login(username=user.username, password="pwd")

        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Log out")
        self.assertContains(response, "View all games")
        self.assertContains(response, "View all characters")
        self.assertContains(response, "Create a new game")
        self.assertContains(response, "Create a new character")
        self.assertNotContains(response, "View your character")
        with self.assertRaises(KeyError):
            response.context["user_character"]

    def test_content_logged_user_existing_character(self):
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.save()
        character = gmodels.Character.objects.create(
            name=utils.generate_random_name(8), user=user
        )
        self.client.login(username=user.username, password="pwd")

        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Log out")
        self.assertContains(response, "View all games")
        self.assertContains(response, "View all characters")
        self.assertContains(response, "Create a new game")
        self.assertNotContains(response, "Create a new character")
        self.assertContains(response, "View your character")
        self.assertEqual(response.context["user_character"], character)


class ListGameViewTest(TestCase):
    path_name = "game-list"

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.save()

        number_of_games = 22
        for i in range(number_of_games):
            gmodels.Game.objects.create(
                name=utils.generate_random_string(20),
                start_date=datetime.now(tz=timezone.utc),
                master=user,
            )

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, gvcommon.ListGameView)

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertTemplateUsed(response, "game/gamelist.html")

    def test_pagination_size(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["game_list"]), 20)

    def test_pagination_size_next_page(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

        response = self.client.get(reverse(self.path_name) + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["game_list"]), 2)

    def test_ordering(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        last_date = 0
        for game in response.context["game_list"]:
            if last_date == 0:
                last_date = game.start_date
            else:
                self.assertTrue(last_date >= game.start_date)
                last_date = game.start_date


class ListCharacterViewTest(TestCase):
    path_name = "character-list"

    @classmethod
    def setUpTestData(cls):
        number_of_characters = 22
        for i in range(number_of_characters):
            user = User.objects.create(username=utils.generate_random_name(5))
            user.set_password("pwd")
            user.save()
            gmodels.Character.objects.create(
                name=utils.generate_random_string(20),
                race=random.choice(gmodels.Character.Race.choices)[0],
                user=user,
            )

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, gvcommon.ListCharacterView
        )

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertTemplateUsed(response, "game/characterlist.html")

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


class GameViewTest(TestCase):
    path_name = "game"

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
                content=f"{game.name} tail{i}",
            )
        number_of_characters = 2
        for i in range(number_of_characters):
            character = gmodels.Character.objects.create(
                game=game,
                name=f"{game.name} character{i}",
                race=random.choice(gmodels.Character.Race.choices)[0],
            )
            gmodels.PendingAction.objects.create(
                game=game,
                character=character,
                action_type=random.choice(gmodels.PendingAction.ActionType.choices)[0],
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
        self.assertQuerySetEqual(
            list(response.context["character_list"]), character_list
        )
        event_list = gmodels.Event.objects.filter(game__name="game1")
        # issubset() is used because of pagination.
        self.assertTrue(set(response.context["event_list"]).issubset(set(event_list)))
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
        self.assertQuerySetEqual(
            list(response.context["character_list"]), character_list
        )
        event_list = gmodels.Event.objects.filter(game__name="game1")
        # issubset() is used because of pagination.
        self.assertTrue(set(response.context["event_list"]).issubset(set(event_list)))
        self.assertEqual(response.context["player"], player)


class CharacterViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        gmodels.Character.objects.create()

    def test_view_mapping(self):
        character = gmodels.Character.objects.last()
        response = self.client.get(character.get_absolute_url())
        self.assertEqual(
            response.resolver_match.func.view_class, gvcommon.DetailCharacterView
        )

    def test_template_mapping(self):
        character = gmodels.Character.objects.last()
        response = self.client.get(character.get_absolute_url())
        self.assertTemplateUsed(response, "game/character.html")


class CreateGameViewTest(TestCase):
    path_name = "game-create"

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.save()
        mmodels.Story.objects.create(title=utils.generate_random_name(20))

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")
        self.story = mmodels.Story.objects.last()

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name, args=(self.story.slug,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, gvcommon.CreateGameView
        )

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name, args=(self.story.slug,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/creategame.html")

    def test_game_creation(self):
        response = self.client.post(reverse(self.path_name, args=(self.story.slug,)))
        self.assertEqual(response.status_code, 302)
        game = gmodels.Game.objects.last()
        self.assertEqual(game.name, self.story.title)
        self.assertEqual(game.status, "P")
        self.assertEqual(game.master, self.user)
        tale = gmodels.Tale.objects.last()
        self.assertEqual(tale.game, game)
        self.assertEqual(tale.message, "The Master created the story.")
        self.assertEqual(tale.content, self.story.synopsis)
        self.assertRedirects(response, reverse("game", args=[game.id]))


class CreateCharacterViewTest(TestCase):
    path_name = "character-create"

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.save()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, gvcommon.CreateCharacterView
        )

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/createcharacter.html")

    def test_character_creation_no_existing_character(self):
        name = utils.generate_random_name(10)
        race = random.choice(gmodels.Character.Race.choices)[0]
        data = {"name": f"{name}", "race": f"{race}"}
        form = gforms.CreateCharacterForm(data)
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        character = gmodels.Character.objects.last()
        self.assertRedirects(response, character.get_absolute_url())
        self.assertEqual(character.name, form.cleaned_data["name"])
        self.assertEqual(character.race, form.cleaned_data["race"])
        self.assertEqual(character.xp, 0)
        self.assertEqual(character.hp, 100)
        self.assertEqual(character.max_hp, 100)
        self.assertEqual(character.user, self.user)

    def test_character_creation_already_existing_character(self):
        gmodels.Character.objects.create(
            name=utils.generate_random_name(5), user=self.user
        )
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)
