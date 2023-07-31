import random

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from faker import Faker

import character.models as cmodels
import game.forms as gforms
import game.models as gmodels
import game.views.player as gvplayer
import utils.testing.factories as utfactories


class DiceLaunchViewTest(TestCase):
    path_name = "dicelaunch-create"

    @classmethod
    def setUpTestData(cls):
        game = utfactories.GameFactory()
        # A game can only start with a minimum number of characters.
        number_of_players = 2
        for _ in range(number_of_players):
            player = utfactories.PlayerFactory(game=game)
            utfactories.PendingActionFactory(game=game, character=player.character)
        game.start()
        game.save()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")
        self.game = gmodels.Game.objects.last()
        self.character = cmodels.Character.objects.last()

    def tearDown(self):
        cache.clear()

    def test_view_mapping(self):
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, gvplayer.DiceLaunchView
        )

    def test_template_mapping(self):
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/dice.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    game_id,
                    self.character.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_character_not_exists(self):
        character_id = random.randint(10000, 99999)
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    character_id,
                ),
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_context_data(self):
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], self.game)
        self.assertEqual(response.context["character"], self.character)

    def test_game_is_under_preparation(self):
        self.game.status = "P"
        self.game.save()
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_game_is_finished(self):
        self.game.end()
        self.game.save()
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_dice_launch(self):
        response = self.client.post(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 302)
        dice_launch = gmodels.DiceLaunch.objects.last()
        self.assertRedirects(
            response,
            reverse(
                "dicelaunch-success",
                args=(
                    self.game.id,
                    self.character.id,
                    dice_launch.id,
                ),
            ),
        )
        self.assertEqual(dice_launch.game, self.game)
        self.assertLessEqual(dice_launch.date.second - timezone.now().second, 2)
        self.assertEqual(
            dice_launch.message,
            f"{self.character} launched a dice: score is {dice_launch.score}!",
        )
        self.assertIsNotNone(dice_launch.score)


class DiceLaunchSuccessViewTest(TestCase):
    path_name = "dicelaunch-success"

    @classmethod
    def setUpTestData(cls):
        game = utfactories.GameFactory()
        number_of_players = 2
        for _ in range(number_of_players):
            player = utfactories.PlayerFactory(game=game)
            utfactories.DiceLaunchFactory(game=game, character=player.character)

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")
        self.game = gmodels.Game.objects.last()
        self.character = cmodels.Character.objects.last()
        self.dice_launch = gmodels.DiceLaunch.objects.last()

    def test_view_mapping(self):
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                    self.dice_launch.id,
                ),
            )
        )
        self.assertEqual(
            response.resolver_match.func.view_class, gvplayer.DiceLaunchSuccessView
        )

    def test_template_mapping(self):
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                    self.dice_launch.id,
                ),
            )
        )
        self.assertTemplateUsed(response, "game/success.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    game_id,
                    self.character.id,
                    self.dice_launch.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_character_not_exists(self):
        character_id = random.randint(10000, 99999)
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    character_id,
                    self.dice_launch.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_view_content(self):
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                    self.dice_launch.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], self.game)
        self.assertEqual(response.context["character"], self.character)
        self.assertEqual(response.context["dice_launch"], self.dice_launch)
        self.assertContains(
            response, f"{self.character.name}, your score is: {self.dice_launch.score}!"
        )


class ChoiceViewTest(TestCase):
    path_name = "choice-create"

    @classmethod
    def setUpTestData(cls):
        game = utfactories.GameFactory()
        # A game can only start with a minimum number of characters.
        number_of_players = 2
        for _ in range(number_of_players):
            player = utfactories.PlayerFactory(game=game)
            utfactories.PendingActionFactory(game=game, character=player.character)
        game.start()
        game.save()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")
        self.game = gmodels.Game.objects.last()
        self.character = cmodels.Character.objects.last()

    def tearDown(self):
        cache.clear()

    def test_view_mapping(self):
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, gvplayer.ChoiceView)

    def test_template_mapping(self):
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/choice.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    game_id,
                    self.character.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_character_not_exists(self):
        character_id = random.randint(10000, 99999)
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    character_id,
                ),
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_context_data(self):
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], self.game)
        self.assertEqual(response.context["character"], self.character)

    def test_game_is_under_preparation(self):
        self.game.status = "P"
        self.game.save()
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_game_is_finished(self):
        self.game.end()
        self.game.save()
        response = self.client.get(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_choice(self):
        fake = Faker()
        selection = fake.text(50)
        data = {"selection": f"{selection}"}
        form = gforms.ChoiceForm(data)
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    self.character.id,
                ),
            ),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        choice = gmodels.Choice.objects.last()
        self.assertRedirects(response, self.game.get_absolute_url())
        self.assertEqual(choice.game, self.game)
        self.assertLessEqual(choice.date.second - timezone.now().second, 2)
        self.assertEqual(
            choice.message,
            f"{self.character} made a choice: {choice.selection}.",
        )
        self.assertEqual(choice.selection, form.cleaned_data["selection"])
