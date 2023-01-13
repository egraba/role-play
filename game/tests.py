from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Game
from .models import Character
from .models import Narrative
from .models import PendingAction
from .models import DiceLaunch

import random
import string


def generate_random_string(length):
    return "".join(random.choice(string.printable) for i in range(length))


def generate_random_name(length):
    return "".join(random.choice(string.ascii_letters) for i in range(length))


def create_game():
    game_name = generate_random_string(random.randint(1, 255))
    return Game.objects.create(name=game_name)


def create_several_games():
    game_list = list()
    n = random.randint(1, 100)
    for i in range(n):
        game_list.append(create_game())
    return game_list


def create_character(game):
    return Character.objects.create(
        name=generate_random_name(255),
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
        message=generate_random_string(1024),
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
    def test_no_game(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No games are available...")

    def test_several_games(self):
        game_list = create_several_games()
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            list(response.context["game_list"]),
            game_list,
        )


class GameViewTests(TestCase):
    def setUp(self):
        self.game = create_game()

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

    def test_view_content(self):
        response = self.client.get(
            reverse("launch_dice", args=[self.game.pk, self.character.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], self.game)
        self.assertEqual(response.context["character"], self.character)
        self.assertContains(response, "! It is your turn.")


class SuccessViewTest(TestCase):
    def setUp(self):
        self.game = create_game()
        self.character = create_character(self.game)
        self.dice_launch = DiceLaunch.objects.create(
            game=self.game, character=self.character, score=random.randint(1, 20)
        )

    def test_view_content(self):
        response = self.client.get(
            reverse(
                "success", args=[self.game.pk, self.character.pk, self.dice_launch.pk]
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], self.game)
        self.assertEqual(response.context["character"], self.character)
        self.assertEqual(response.context["dice_launch"], self.dice_launch)
        self.assertContains(
            response, f"{self.character.name}, your score is: {self.dice_launch.score}!"
        )
