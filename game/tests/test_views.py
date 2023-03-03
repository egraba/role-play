import random
from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from game.models import Character, Choice, DiceLaunch, Game, Narrative, PendingAction
from game.tests import utils
from game.views import (
    AddCharacterView,
    ChoiceSuccessView,
    ChoiceView,
    DiceLaunchSuccessView,
    DiceLaunchView,
    GameView,
    IndexView,
)


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
        message=utils.generate_random_string(500),
    )


def create_several_narratives(game):
    narrative_list = list()
    n = random.randint(1, 2)
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
            Game.objects.create(
                name=utils.generate_random_string(20),
                start_date=datetime.now(tz=timezone.utc),
            )

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
    @classmethod
    def setUpTestData(cls):
        Game.objects.create(name=utils.generate_random_string(20))
        game = Game.objects.last()
        number_of_narratives = 22
        for i in range(number_of_narratives):
            Narrative.objects.create(
                game=game,
                date=datetime.now(tz=timezone.utc),
                message=utils.generate_random_string(500),
            )

    def test_view_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.resolver_match.func.view_class, GameView)

    def test_pagination_size(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["narrative_list"]), 20)

    def test_pagination_size_next_page(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]) + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["narrative_list"]), 2)

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

    def test_game_exists(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse("game", args=[game_id]))
        self.assertEqual(response.status_code, 404)

    def test_game_several_characters(self):
        game = Game.objects.last()
        character_list = create_several_characters(game)
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            list(response.context["character_list"]),
            character_list,
        )

    def test_game_several_pending_actions(self):
        game = Game.objects.last()
        character_list = create_several_characters(game)
        narrative_list = create_several_narratives(game)
        narrative = narrative_list.pop()
        pending_action_list = list()
        for character in character_list:
            pending_action = create_pending_action(game, narrative, character)
            pending_action_list.append(pending_action)
        response = self.client.get(reverse("game", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            list(response.context["pending_action_list"]),
            list(pending_action_list),
        )


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


class DiceLaunchViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        Character.objects.create(
            name=utils.generate_random_name(255),
            game=game,
            race=random.choice(Character.RACES)[0],
        )

    def test_view_mapping_ok(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(reverse("launch_dice", args=[game.id, character.id]))
        self.assertEqual(response.resolver_match.func.view_class, DiceLaunchView)

    def test_view_content(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(reverse("launch_dice", args=[game.id, character.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], game)
        self.assertEqual(response.context["character"], character)
        self.assertContains(response, "! It is your turn.")


class ChoiceViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        Character.objects.create(
            name=utils.generate_random_name(255),
            game=game,
            race=random.choice(Character.RACES)[0],
        )

    def test_view_mapping_ok(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(reverse("make_choice", args=[game.id, character.id]))
        self.assertEqual(response.resolver_match.func.view_class, ChoiceView)

    def test_view_content(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(reverse("make_choice", args=[game.id, character.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], game)
        self.assertEqual(response.context["character"], character)


class DiceLaunchSuccessViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        character = Character.objects.create(
            name=utils.generate_random_name(255),
            game=game,
            race=random.choice(Character.RACES)[0],
        )
        DiceLaunch.objects.create(
            game=game, character=character, score=random.randint(1, 20)
        )

    def test_view_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        dice_launch = DiceLaunch.objects.last()
        response = self.client.get(
            reverse(
                "dice_success",
                args=[game.id, character.id, dice_launch.id],
            )
        )
        self.assertEqual(response.resolver_match.func.view_class, DiceLaunchSuccessView)

    def test_view_content(self):
        game = Game.objects.last()
        character = Character.objects.last()
        dice_launch = DiceLaunch.objects.last()
        response = self.client.get(
            reverse(
                "dice_success",
                args=[game.id, character.id, dice_launch.id],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], game)
        self.assertEqual(response.context["character"], character)
        self.assertEqual(response.context["dice_launch"], dice_launch)
        self.assertContains(
            response, f"{character.name}, your score is: {dice_launch.score}!"
        )


class ChoiceSuccessViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        character = Character.objects.create(
            name=utils.generate_random_name(255),
            game=game,
            race=random.choice(Character.RACES)[0],
        )
        Choice.objects.create(
            game=game,
            character=character,
            selection=utils.generate_random_name(255),
        )

    def test_view_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        choice = Choice.objects.last()
        response = self.client.get(
            reverse("choice_success", args=[game.id, character.id, choice.id])
        )
        self.assertEqual(response.resolver_match.func.view_class, ChoiceSuccessView)

    def test_view_content(self):
        game = Game.objects.last()
        character = Character.objects.last()
        choice = Choice.objects.last()
        response = self.client.get(
            reverse("choice_success", args=[game.id, character.id, choice.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], game)
        self.assertEqual(response.context["character"], character)
        self.assertEqual(response.context["choice"], choice)
        self.assertContains(response, f"{choice.selection}")
