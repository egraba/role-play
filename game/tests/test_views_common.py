import random
from datetime import datetime, timezone

from django.contrib.auth.models import User
from django.http import Http404
from django.test import TestCase
from django.urls import reverse

import character.models as cmodels
import game.models as gmodels
import game.views.common as gvcommon
import master.models as mmodels
import utils.testing.random as utrandom
import utils.testing.users as utusers


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
        user = User.objects.create(username=utrandom.ascii_letters_string(5))
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
        user = User.objects.create(username=utrandom.ascii_letters_string(5))
        user.set_password("pwd")
        user.save()
        character = cmodels.Character.objects.create(
            name=utrandom.ascii_letters_string(8)
        )
        gmodels.Player.objects.create(character=character, user=user)
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


class GameListViewTest(TestCase):
    path_name = "game-list"

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username=utrandom.ascii_letters_string(5))
        user.set_password("pwd")
        user.save()

        number_of_games = 22
        for i in range(number_of_games):
            gmodels.Game.objects.create(
                name=utrandom.printable_string(20),
                start_date=datetime.now(tz=timezone.utc),
                master=user,
            )

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, gvcommon.GameListView)

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertTemplateUsed(response, "game/game_list.html")

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
        last_date = datetime.now(tz=timezone.utc).second
        for game in response.context["game_list"]:
            if last_date == datetime.now(tz=timezone.utc).second:
                last_date = game.start_date
            else:
                self.assertTrue(last_date >= game.start_date)
                last_date = game.start_date

    def test_content_no_game(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")
        gmodels.Game.objects.all().delete()

        response = self.client.get(reverse(self.path_name))
        self.assertContains(response, "There is no game available...")


class GameViewTest(TestCase):
    path_name = "game"

    @classmethod
    def setUpTestData(cls):
        master = utusers.create_user("master")

        game = gmodels.Game.objects.create(name="game1", master=master)
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
            character = cmodels.Character.objects.create(
                name=f"{game.name} character{i}",
                race=random.choice(cmodels.Character.Race.choices)[0],
            )
            user = User.objects.create(username=f"user{i}")
            gmodels.Player.objects.create(user=user, character=character, game=game)
            gmodels.PendingAction.objects.create(
                game=game,
                character=character,
                action_type=gmodels.PendingAction.ActionType.choices[i][0],
                message=f"{game.name} pending_action{i}",
            )

    def setUp(self):
        self.user = User.objects.get(username="master")
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
        number_of_characters = 3
        for i in range(number_of_characters):
            character = cmodels.Character.objects.create(
                name=utrandom.ascii_letters_string(7)
            )
            gmodels.Player.objects.create(character=character, game=game)
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
            character = cmodels.Character.objects.create(name=f"character{i}")
            gmodels.Player.objects.create(game=game, character=character)
            gmodels.Event.objects.create(game=game)
            gmodels.PendingAction.objects.create(game=game, character=character)

        game = gmodels.Game.objects.filter(name="game1").last()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)

        tale_list = gmodels.Tale.objects.filter(game__name="game1")
        tale = tale_list.last()
        self.assertEqual(response.context["tale"], tale)
        character_list = cmodels.Character.objects.filter(player__game__name="game1")
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
            character = cmodels.Character.objects.create(name=f"character{i}")
            gmodels.Player.objects.create(game=game, character=character)
            gmodels.Event.objects.create(game=game)
            gmodels.PendingAction.objects.create(game=game, character=character)

        player = gmodels.Player.objects.filter(character__name="character1").get()
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
        character_list = cmodels.Character.objects.filter(player__game__name="game1")
        self.assertQuerySetEqual(
            list(response.context["character_list"]), character_list
        )
        event_list = gmodels.Event.objects.filter(game__name="game1")
        # issubset() is used because of pagination.
        self.assertTrue(set(response.context["event_list"]).issubset(set(event_list)))
        self.assertEqual(response.context["player"], player)

    def test_content_character_is_current_user(self):
        player = gmodels.Player.objects.last()
        character = cmodels.Character.objects.get(player=player)
        player.user = self.user
        player.save()
        game = gmodels.Game.objects.get(player__character=character)
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "(you)")

    def test_content_no_events(self):
        game = gmodels.Game.objects.last()
        gmodels.Event.objects.filter(game=game).delete()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The story did not start yet...")

    def test_content_game_is_finished(self):
        game = gmodels.Game.objects.create(
            master=self.user, status=gmodels.Game.Status.FINISHED
        )
        response = self.client.get(game.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The game is finished.")

    def test_content_pending_action_launch_dice(self):
        game = gmodels.Game.objects.get(name="game1")
        self.client.login(username="user0")
        response = self.client.get(game.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Launch dice")

    def test_content_pending_action_make_choice(self):
        game = gmodels.Game.objects.get(name="game1")
        self.client.login(username="user1")
        response = self.client.get(game.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Make choice")


class GameCreateViewTest(TestCase):
    path_name = "game-create"

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username=utrandom.ascii_letters_string(5))
        user.set_password("pwd")
        user.save()
        mmodels.Story.objects.create(title=utrandom.ascii_letters_string(20))

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")
        self.story = mmodels.Story.objects.last()

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name, args=(self.story.slug,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, gvcommon.GameCreateView
        )

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name, args=(self.story.slug,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/game_create.html")

    def test_game_creation(self):
        response = self.client.post(reverse(self.path_name, args=(self.story.slug,)))
        self.assertEqual(response.status_code, 302)
        game = gmodels.Game.objects.last()
        self.assertRedirects(response, game.get_absolute_url())
        self.assertEqual(game.name, self.story.title)
        self.assertEqual(game.status, "P")
        self.assertEqual(game.master, self.user)
        tale = gmodels.Tale.objects.last()
        self.assertEqual(tale.game, game)
        self.assertEqual(tale.message, "The Master created the story.")
        self.assertEqual(tale.content, self.story.synopsis)

    def test_game_creation_story_does_not_exist(self):
        fake_slug = utrandom.ascii_letters_string(5)
        response = self.client.post(reverse(self.path_name, args=(fake_slug,)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("game-create-error", args=(fake_slug,)))


class GameCreateErrorViewTest(TestCase):
    path_name = "game-create-error"
    fake_slug = utrandom.ascii_letters_string(5)

    @classmethod
    def setUpTestData(cls):
        utusers.create_user()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name, args=(self.fake_slug,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, gvcommon.GameCreateErrorView
        )

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name, args=(self.fake_slug,)))
        self.assertTemplateUsed(response, "game/game_create_error.html")
