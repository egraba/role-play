import random

from django.contrib.auth.models import Permission, User
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from game.forms import ChoiceForm, CreateCharacterForm
from game.models import Character, Choice, DiceLaunch, Game, PendingAction
from game.tests import utils
from game.views.player import (
    ChoiceView,
    CreateCharacterView,
    DiceLaunchSuccessView,
    DiceLaunchView,
)


class CreateCharacterViewTest(TestCase):
    path_name = "character-create"

    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="add_character")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, CreateCharacterView)

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/createcharacter.html")

    def test_character_creation_no_existing_character(self):
        name = utils.generate_random_name(10)
        race = random.choice(Character.RACES)[0]
        data = {"name": f"{name}", "race": f"{race}"}
        form = CreateCharacterForm(data)
        self.assertTrue(form.is_valid())
        response = self.client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        character = Character.objects.last()
        self.assertRedirects(
            response, reverse("character-detail", args=(character.id,))
        )
        self.assertEqual(character.name, form.cleaned_data["name"])
        self.assertEqual(character.race, form.cleaned_data["race"])
        self.assertEqual(character.xp, 0)
        self.assertEqual(character.hp, 100)
        self.assertEqual(character.max_hp, 100)
        self.assertEqual(character.user, self.user)

    def test_character_creation_already_existing_character(self):
        self.client.get(reverse(self.path_name))
        self.assertRaises(PermissionDenied)


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

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        character = Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game_id, character.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_character_not_exists(self):
        game = Game.objects.last()
        character_id = random.randint(10000, 99999)
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character_id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

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
        self.assertLessEqual(dice_launch.date.second - timezone.now().second, 2)
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

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        character = Character.objects.last()
        dice_launch = DiceLaunch.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game_id, character.id, dice_launch.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_character_not_exists(self):
        game = Game.objects.last()
        character_id = random.randint(10000, 99999)
        dice_launch = DiceLaunch.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character_id, dice_launch.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

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

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        character = Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game_id, character.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_character_not_exists(self):
        game = Game.objects.last()
        character_id = random.randint(10000, 99999)
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character_id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

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

    def test_choice(self):
        selection = utils.generate_random_string(50)
        data = {"selection": f"{selection}"}
        form = ChoiceForm(data)
        self.assertTrue(form.is_valid())
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.post(
            reverse(self.path_name, args=[game.id, character.id]),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        choice = Choice.objects.last()
        self.assertRedirects(
            response,
            reverse("game", args=[game.id]),
        )
        self.assertEqual(choice.game, game)
        self.assertLessEqual(choice.date.second - timezone.now().second, 2)
        self.assertEqual(
            choice.message,
            f"{character} made a choice: {choice.selection}.",
        )
        self.assertEqual(choice.selection, form.cleaned_data["selection"])
