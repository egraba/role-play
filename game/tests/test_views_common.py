import random
from datetime import datetime, timezone

from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import Http404
from django.test import TestCase
from django.urls import reverse
from faker import Faker

import game.models as gmodels
import game.views.common as gvcommon
import utils.testing.factories as utfactories
from character.models.character import Character


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
        user = utfactories.UserFactory()
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
        character = utfactories.CharacterFactory()
        self.client.login(username=character.user.username, password="pwd")

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
        number_of_games = 22
        for _ in range(number_of_games):
            utfactories.GameFactory(
                start_date=datetime.now(tz=timezone.utc),
                master__user__username="master-game-list-view",
            )

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

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
        self.user = User.objects.get(username="master-game-list-view")
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
    @classmethod
    def setUpTestData(cls):
        game = utfactories.GameFactory(master__user__username="master-game-view")
        number_of_events = 10
        for _ in range(number_of_events):
            utfactories.EventFactory(game=game)
        number_of_quests = 3
        for _ in range(number_of_quests):
            utfactories.QuestFactory(game=game)
        number_of_players = 8
        for _ in range(number_of_players):
            utfactories.PlayerFactory(game=game)

    def setUp(self):
        self.user = User.objects.get(username="master-game-view")
        self.client.login(username=self.user.username, password="pwd")
        self.game = gmodels.Game.objects.last()

    def tearDown(self):
        cache.clear()

    def test_view_mapping(self):
        response = self.client.get(self.game.get_absolute_url())
        self.assertEqual(response.resolver_match.func.view_class, gvcommon.GameView)

    def test_template_mapping(self):
        response = self.client.get(self.game.get_absolute_url())
        self.assertTemplateUsed(response, "game/game.html")

    def test_pagination_size(self):
        response = self.client.get(self.game.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["event_list"]), 10)

    def test_pagination_size_next_page(self):
        response = self.client.get(self.game.get_absolute_url() + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["event_list"]), 4)  # Inherited events

    def test_ordering_character_name_ascending(self):
        response = self.client.get(self.game.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        last_name = ""
        for character in response.context["character_list"]:
            if last_name == "":
                last_name = character.name.upper()
            else:
                self.assertTrue(last_name <= character.name)
                last_name = character.name.upper()

    def test_ordering_event_date_descending(self):
        response = self.client.get(self.game.get_absolute_url())
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

    def test_game_last_quest(self):
        quest = gmodels.Quest.objects.filter(game=self.game).last()
        response = self.client.get(self.game.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["quest"], quest)

    def test_context_data_master(self):
        response = self.client.get(self.game.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        quest_list = gmodels.Quest.objects.filter(game=self.game)
        quest = quest_list.last()
        self.assertEqual(response.context["quest"], quest)
        character_list = Character.objects.filter(player__game=self.game)
        self.assertQuerySetEqual(
            list(response.context["character_list"]), list(character_list)
        )
        event_list = gmodels.Event.objects.filter(game=self.game)
        # issubset() is used because of pagination.
        self.assertTrue(set(response.context["event_list"]).issubset(set(event_list)))
        with self.assertRaises(KeyError):
            response.context["player"]

    def test_context_data_player(self):
        self.client.logout()
        # Log as a player
        character = Character.objects.filter(player__game=self.game).last()
        user = character.user
        self.client.login(username=user.username, password="pwd")
        response = self.client.get(self.game.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        quest_list = gmodels.Quest.objects.filter(game=self.game)
        quest = quest_list.last()
        self.assertEqual(response.context["quest"], quest)
        character_list = Character.objects.filter(player__game=self.game)
        self.assertQuerySetEqual(
            list(response.context["character_list"]), list(character_list)
        )
        event_list = gmodels.Event.objects.filter(game=self.game)
        # issubset() is used because of pagination.
        self.assertTrue(set(response.context["event_list"]).issubset(set(event_list)))
        player = gmodels.Player.objects.get(game=self.game, character__user=user)
        self.assertEqual(response.context["player"], player)

    def test_content_character_is_current_user(self):
        self.client.logout()
        # Log as a player
        character = Character.objects.filter(player__game=self.game).last()
        user = character.user
        self.client.login(username=user.username, password="pwd")
        response = self.client.get(self.game.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "played by you")

    def test_content_no_events(self):
        gmodels.Event.objects.filter(game=self.game).delete()
        response = self.client.get(self.game.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The campaign did not start yet...")


class GameCreateViewTest(TestCase):
    path_name = "game-create"

    def setUp(self):
        self.user = utfactories.UserFactory(username="game-create")
        self.client.login(username=self.user.username, password="pwd")
        self.campaign = utfactories.CampaignFactory()

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name, args=(self.campaign.slug,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, gvcommon.GameCreateView
        )

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name, args=(self.campaign.slug,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/game_create.html")

    def test_game_creation(self):
        response = self.client.post(reverse(self.path_name, args=(self.campaign.slug,)))
        self.assertEqual(response.status_code, 302)
        game = gmodels.Game.objects.last()
        self.assertRedirects(response, game.get_absolute_url())
        self.assertEqual(game.name, f"{self.campaign.title} #{game.id}")
        self.assertEqual(game.status, "P")
        self.assertEqual(game.master.user, self.user)
        quest = gmodels.Quest.objects.last()
        self.assertEqual(quest.game, game)
        self.assertEqual(quest.message, "The Master created the campaign.")
        self.assertEqual(quest.content, self.campaign.synopsis)

    def test_game_creation_campaign_does_not_exist(self):
        fake = Faker()
        fake_slug = fake.slug()
        response = self.client.post(reverse(self.path_name, args=(fake_slug,)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("game-create-error", args=(fake_slug,)))


class GameCreateErrorViewTest(TestCase):
    path_name = "game-create-error"
    fake = Faker()
    fake_slug = fake.slug()

    def setUp(self):
        self.user = utfactories.UserFactory(username="game-create-error")
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
