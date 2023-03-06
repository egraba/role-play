import random

from django.test import TestCase
from django.urls import reverse

from game.models import Character, Choice, DiceLaunch, Game
from game.tests import utils
from game.views.player import (
    ChoiceSuccessView,
    ChoiceView,
    DiceLaunchSuccessView,
    DiceLaunchView,
)


class DiceLaunchViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        Character.objects.create(
            name=utils.generate_random_name(100),
            game=game,
            race=random.choice(Character.RACES)[0],
        )

    def test_view_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(reverse("launch_dice", args=[game.id, character.id]))
        self.assertEqual(response.resolver_match.func.view_class, DiceLaunchView)

    def test_template_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(reverse("launch_dice", args=[game.id, character.id]))
        self.assertTemplateUsed(response, "game/dice.html")

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
            name=utils.generate_random_name(100),
            game=game,
            race=random.choice(Character.RACES)[0],
        )

    def test_view_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(reverse("make_choice", args=[game.id, character.id]))
        self.assertEqual(response.resolver_match.func.view_class, ChoiceView)

    def test_template_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(reverse("make_choice", args=[game.id, character.id]))
        self.assertTemplateUsed(response, "game/choice.html")

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
            name=utils.generate_random_name(100),
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

    def test_template_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        dice_launch = DiceLaunch.objects.last()
        response = self.client.get(
            reverse("dice_success", args=[game.id, character.id, dice_launch.id])
        )
        self.assertTemplateUsed(response, "game/success.html")

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
            name=utils.generate_random_name(100),
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

    def test_template_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        choice = Choice.objects.last()
        response = self.client.get(
            reverse("choice_success", args=[game.id, character.id, choice.id])
        )
        self.assertTemplateUsed(response, "game/success.html")

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
