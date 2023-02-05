import random
from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from game.models import Character, Choice, DiceLaunch, Game, Narrative, PendingAction
from game.tests import utils
from game.views import (
    ChoiceSuccessView,
    ChoiceView,
    DiceLaunchSuccessView,
    DiceLaunchView,
    GameView,
    IndexView,
)


def create_game():
    game_name = utils.generate_random_string(random.randint(1, 255))
    return Game.objects.create(name=game_name)


def create_several_games():
    game_list = list()
    n = random.randint(1, 100)
    for i in range(n):
        game_list.append(create_game())
    return game_list


def create_character(game):
    return Character.objects.create(
        name=utils.generate_random_name(255),
        game=game,
        race=random.choice(Character.RACES)[0],
    )


def create_several_characters(game):
    character_list = list()
    n = random.randint(2, 10)
    for i in range(n):
        character_list.append(create_character(game))
    return character_list


def create_narrative(game):
    return Narrative.objects.create(
        date=datetime.now(tz=timezone.utc),
        game=game,
        message=utils.generate_random_string(1024),
    )


def create_several_narratives(game):
    narrative_list = list()
    n = random.randint(10, 100)
    for i in range(n):
        narrative_list.append(create_narrative(game))
    return narrative_list


def create_pending_action(game, narrative, character):
    return PendingAction.objects.create(
        game=game,
        narrative=narrative,
        character=character,
        action_type=random.choice(PendingAction.ACTION_TYPES)[0],
    )


class IndexViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_games = 12
        for i in range(number_of_games):
            Game.objects.create(name=utils.generate_random_name(20))

    def test_view_mapping(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, IndexView)

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


class GameViewTests(TestCase):
    def setUp(self):
        self.game = create_game()

    def test_view_mapping_ok(self):
        response = self.client.get(reverse("game", args=[self.game.pk]))
        self.assertEqual(response.resolver_match.func.view_class, GameView)

    def test_game_exists(self):
        response = self.client.get(reverse("game", args=[self.game.pk]))
        self.assertEqual(response.status_code, 200)

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse("game", args=[game_id]))
        self.assertEqual(response.status_code, 404)

    def test_game_no_characters(self):
        response = self.client.get(reverse("game", args=[self.game.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No characters for this game...")

    def test_game_several_characters(self):
        character_list = create_several_characters(self.game)
        response = self.client.get(reverse("game", args=[self.game.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            list(response.context["character_list"]),
            character_list,
        )

    def test_game_no_narrative(self):
        response = self.client.get(reverse("game", args=[self.game.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The story did not start yet...")

    def test_game_several_narratives(self):
        narrative_list = create_several_narratives(self.game)
        response = self.client.get(reverse("game", args=[self.game.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            list(response.context["narrative_list"]),
            narrative_list,
        )

    def test_game_no_pending_actions(self):
        response = self.client.get(reverse("game", args=[self.game.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            list(response.context["pending_action_list"]),
            list(),
        )

    def test_game_several_pending_actions(self):
        character_list = create_several_characters(self.game)
        narrative_list = create_several_narratives(self.game)
        narrative = narrative_list.pop()
        pending_action_list = list()
        for character in character_list:
            pending_action = create_pending_action(self.game, narrative, character)
            pending_action_list.append(pending_action)
        response = self.client.get(reverse("game", args=[self.game.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            list(response.context["pending_action_list"]),
            list(pending_action_list),
        )


class DiceLaunchViewTest(TestCase):
    def setUp(self):
        self.game = create_game()
        self.character = create_character(self.game)

    def test_view_mapping_ok(self):
        response = self.client.get(
            reverse("launch_dice", args=[self.game.pk, self.character.pk])
        )
        self.assertEqual(response.resolver_match.func.view_class, DiceLaunchView)

    def test_view_content(self):
        response = self.client.get(
            reverse("launch_dice", args=[self.game.pk, self.character.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], self.game)
        self.assertEqual(response.context["character"], self.character)
        self.assertContains(response, "! It is your turn.")


class ChoiceViewTest(TestCase):
    def setUp(self):
        self.game = create_game()
        self.character = create_character(self.game)

    def test_view_mapping_ok(self):
        response = self.client.get(
            reverse("make_choice", args=[self.game.pk, self.character.pk])
        )
        self.assertEqual(response.resolver_match.func.view_class, ChoiceView)

    def test_view_content(self):
        response = self.client.get(
            reverse("make_choice", args=[self.game.pk, self.character.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], self.game)
        self.assertEqual(response.context["character"], self.character)


class DiceLaunchSuccessViewTest(TestCase):
    def setUp(self):
        self.game = create_game()
        self.character = create_character(self.game)
        self.dice_launch = DiceLaunch.objects.create(
            game=self.game, character=self.character, score=random.randint(1, 20)
        )

    def test_view_mapping_ok(self):
        response = self.client.get(
            reverse(
                "dice_success",
                args=[self.game.pk, self.character.pk, self.dice_launch.pk],
            )
        )
        self.assertEqual(response.resolver_match.func.view_class, DiceLaunchSuccessView)

    def test_view_content(self):
        response = self.client.get(
            reverse(
                "dice_success",
                args=[self.game.pk, self.character.pk, self.dice_launch.pk],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], self.game)
        self.assertEqual(response.context["character"], self.character)
        self.assertEqual(response.context["dice_launch"], self.dice_launch)
        self.assertContains(
            response, f"{self.character.name}, your score is: {self.dice_launch.score}!"
        )


class ChoiceSuccessViewTest(TestCase):
    def setUp(self):
        self.game = create_game()
        self.character = create_character(self.game)
        self.choice = Choice.objects.create(
            game=self.game,
            character=self.character,
            selection=utils.generate_random_name(255),
        )

    def test_view_mapping_ok(self):
        response = self.client.get(
            reverse(
                "choice_success", args=[self.game.pk, self.character.pk, self.choice.pk]
            )
        )
        self.assertEqual(response.resolver_match.func.view_class, ChoiceSuccessView)

    def test_view_content(self):
        response = self.client.get(
            reverse(
                "choice_success", args=[self.game.pk, self.character.pk, self.choice.pk]
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], self.game)
        self.assertEqual(response.context["character"], self.character)
        self.assertEqual(response.context["choice"], self.choice)
        self.assertContains(response, f"{self.choice.selection}")
