import random

from django.contrib.auth.models import Permission, User
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from game.models import Character, Choice, DiceLaunch, Game, PendingAction
from game.tests import utils
from game.views.player import (
    ChoiceSuccessView,
    ChoiceView,
    DiceLaunchSuccessView,
    DiceLaunchView,
)


class DiceLaunchViewTest(TestCase):
    path_name = "dicelaunch-create"

    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="add_dicelaunch")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()
        game = Game.objects.create()
        number_of_characters = 2
        for i in range(number_of_characters):
            character = Character.objects.create(
                name=utils.generate_random_name(5),
                game=game,
            )
            PendingAction.objects.create(game=game, character=character)
        game.start()
        game.save()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, DiceLaunchView)

    def test_template_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/dice.html")

    def test_context_data(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], game)
        self.assertEqual(response.context["character"], character)

    def test_game_is_under_preparation(self):
        game = Game.objects.create()
        character = Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_game_is_finished(self):
        game = Game.objects.last()
        character = Character.objects.last()
        game.end()
        game.save()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_dice_launch(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.post(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 302)
        dice_launch = DiceLaunch.objects.last()
        self.assertRedirects(
            response,
            reverse("dicelaunch-success", args=[game.id, character.id, dice_launch.id]),
        )
        self.assertEqual(dice_launch.game, game)
        self.assertEqual(dice_launch.date.second, timezone.now().second)
        self.assertEqual(
            dice_launch.message,
            f"{character} launched a dice: score is {dice_launch.score}!",
        )
        self.assertIsNotNone(dice_launch.score)


class DiceLaunchSuccessViewTest(TestCase):
    path_name = "dicelaunch-success"

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
                self.path_name,
                args=[game.id, character.id, dice_launch.id],
            )
        )
        self.assertEqual(response.resolver_match.func.view_class, DiceLaunchSuccessView)

    def test_template_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        dice_launch = DiceLaunch.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id, dice_launch.id])
        )
        self.assertTemplateUsed(response, "game/success.html")

    def test_view_content(self):
        game = Game.objects.last()
        character = Character.objects.last()
        dice_launch = DiceLaunch.objects.last()
        response = self.client.get(
            reverse(
                self.path_name,
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


class ChoiceViewTest(TestCase):
    path_name = "choice-create"

    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="add_choice")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()
        game = Game.objects.create()
        number_of_characters = 2
        for i in range(number_of_characters):
            character = Character.objects.create(
                name=utils.generate_random_name(5),
                game=game,
            )
            PendingAction.objects.create(game=game, character=character)
        game.start()
        game.save()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, ChoiceView)

    def test_template_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/choice.html")

    def test_context_data(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], game)
        self.assertEqual(response.context["character"], character)

    def test_game_is_under_preparation(self):
        game = Game.objects.create()
        character = Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_game_is_finished(self):
        game = Game.objects.last()
        character = Character.objects.last()
        game.end()
        game.save()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)


class ChoiceSuccessViewTest(TestCase):
    path_name = "choice-success"

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
            reverse(self.path_name, args=[game.id, character.id, choice.id])
        )
        self.assertEqual(response.resolver_match.func.view_class, ChoiceSuccessView)

    def test_template_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        choice = Choice.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id, choice.id])
        )
        self.assertTemplateUsed(response, "game/success.html")

    def test_view_content(self):
        game = Game.objects.last()
        character = Character.objects.last()
        choice = Choice.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id, choice.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], game)
        self.assertEqual(response.context["character"], character)
        self.assertEqual(response.context["choice"], choice)
        self.assertContains(response, f"{choice.selection}")
