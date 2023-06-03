import random

from django.contrib.auth.models import Permission, User
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.forms import ValidationError
from django.http import Http404
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

import game.forms as gforms
import game.models as gmodels
import game.views.master as gvmaster
from game.tests import utils


class CreateGameViewTest(TestCase):
    path_name = "game-create"

    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="add_game")
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
        self.assertEqual(
            response.resolver_match.func.view_class, gvmaster.CreateGameView
        )

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/creategame.html")

    def test_game_creation(self):
        name = utils.generate_random_name(20)
        description = utils.generate_random_string(100)
        data = {"name": f"{name}", "description": f"{description}"}
        form = gforms.CreateGameForm(data)
        self.assertTrue(form.is_valid())

        response = self.client.post(reverse(self.path_name), data=form.cleaned_data)
        self.assertEqual(response.status_code, 302)
        game = gmodels.Game.objects.last()
        self.assertEqual(game.name, name)
        self.assertEqual(game.status, "P")
        self.assertEqual(game.user, self.user)
        tale = gmodels.Tale.objects.last()
        self.assertEqual(tale.game, game)
        self.assertEqual(tale.message, "The Master created the story.")
        self.assertEqual(tale.content, form.cleaned_data["description"])
        self.assertRedirects(response, reverse("game", args=[game.id]))


class AddCharacterViewTest(TestCase):
    path_name = "game-add-character"

    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="change_character")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()

        game = gmodels.Game.objects.create()
        number_of_characters_with_game = 5
        number_of_characters_without_game = 12
        for i in range(number_of_characters_with_game):
            gmodels.Character.objects.create(
                name=utils.generate_random_name(10),
                game=game,
                race=random.choice(gmodels.Character.RACES)[0],
            )
        for i in range(number_of_characters_without_game):
            gmodels.Character.objects.create(
                name=utils.generate_random_name(10),
                race=random.choice(gmodels.Character.RACES)[0],
                xp=random.randint(1, 100),
            )

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = gmodels.Game.objects.last()
        response = self.client.get(reverse(self.path_name, args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, gvmaster.AddCharacterView
        )

    def test_template_mapping(self):
        game = gmodels.Game.objects.last()
        response = self.client.get(reverse(self.path_name, args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/addcharacter.html")

    def test_pagination_size(self):
        game = gmodels.Game.objects.last()
        response = self.client.get(reverse(self.path_name, args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["character_list"]), 10)

    def test_pagination_size_next_page(self):
        game = gmodels.Game.objects.last()
        response = self.client.get(reverse(self.path_name, args=[game.id]) + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["character_list"]), 2)

    def test_ordering(self):
        game = gmodels.Game.objects.last()
        response = self.client.get(reverse(self.path_name, args=[game.id]))
        self.assertEqual(response.status_code, 200)
        last_xp = 0
        for character in response.context["character_list"]:
            if last_xp == 0:
                last_xp = character.xp
            else:
                self.assertTrue(last_xp >= character.xp)
                last_xp = character.xp

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse(self.path_name, args=[game_id]))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_context_data(self):
        game = gmodels.Game.objects.last()
        character_list = gmodels.Character.objects.filter(game=None)
        response = self.client.get(reverse(self.path_name, args=(game.id,)))
        self.assertTrue(
            set(response.context["character_list"]).issubset(character_list)
        )

    def test_context_data_all_characters_already_assigned(self):
        game = gmodels.Game.objects.last()
        character_list = gmodels.Character.objects.filter(game=None)
        for character in character_list:
            character.game = game
            character.save()
        response = self.client.get(reverse(self.path_name, args=(game.id,)))
        self.assertFalse(response.context["character_list"])


class AddCharacterConfirmViewTest(TestCase):
    path_name = "game-add-character-confirm"

    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="change_character")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()

        gmodels.Game.objects.create()
        gmodels.Character.objects.create(name=utils.generate_random_name(5))

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, gvmaster.AddCharacterConfirmView
        )

    def test_template_mapping(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/addcharacterconfirm.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game_id, character.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_character_added_to_game(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        response = self.client.post(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("game", args=[game.id]))
        character = gmodels.Character.objects.last()
        self.assertEqual(character.game, game)
        event = gmodels.Event.objects.last()
        self.assertLessEqual(event.date.second - timezone.now().second, 2)
        self.assertEqual(event.game, game)
        self.assertEqual(event.message, f"{character} was added to the game.")


class StartGameViewTest(TestCase):
    path_name = "game-start"

    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="change_game")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()

        gmodels.Game.objects.create()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = gmodels.Game.objects.last()
        response = self.client.get(reverse(self.path_name, args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, gvmaster.StartGameView
        )

    def test_template_mapping(self):
        game = gmodels.Game.objects.last()
        response = self.client.get(reverse(self.path_name, args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/startgame.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse(self.path_name, args=[game_id]))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_game_start_ok(self):
        game = gmodels.Game.objects.last()
        number_of_characters = 2
        for i in range(number_of_characters):
            gmodels.Character.objects.create(
                game=game, name=utils.generate_random_name(5)
            )
        response = self.client.post(reverse(self.path_name, args=[game.id]))
        self.assertEqual(response.status_code, 302)
        game = gmodels.Game.objects.last()
        self.assertEqual(game.status, "O")
        event = gmodels.Event.objects.last()
        self.assertLessEqual(event.date.second - timezone.now().second, 2)
        self.assertEqual(event.game, game)
        self.assertEqual(event.message, "The game started.")

    def test_game_start_not_enough_characters(self):
        game = gmodels.Game.objects.last()
        number_of_characters = 1
        for i in range(number_of_characters):
            gmodels.Character.objects.create(
                game=game, name=utils.generate_random_name(5)
            )
        response = self.client.post(reverse(self.path_name, args=[game.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRaises(PermissionDenied)
        game = gmodels.Game.objects.last()
        self.assertEqual(game.status, "P")
        self.assertRedirects(response, reverse("game-start-error", args=(game.id,)))


class EndGameViewTest(TestCase):
    path_name = "game-end"

    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="change_game")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()

        gmodels.Game.objects.create()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = gmodels.Game.objects.last()
        response = self.client.get(reverse(self.path_name, args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, gvmaster.EndGameView)

    def test_template_mapping(self):
        game = gmodels.Game.objects.last()
        response = self.client.get(reverse(self.path_name, args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/endgame.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse(self.path_name, args=[game_id]))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_game_end_ok(self):
        game = gmodels.Game.objects.last()
        number_of_characters = 5
        for i in range(number_of_characters):
            gmodels.Character.objects.create(
                game=game, name=utils.generate_random_name(5)
            )
        game.start()
        game.save()

        response = self.client.post(reverse(self.path_name, args=[game.id]))
        self.assertEqual(response.status_code, 302)
        game = gmodels.Game.objects.last()
        self.assertEqual(game.status, "F")
        self.assertTrue(gmodels.Character.objects.filter(game=game).count() == 0)
        event = gmodels.Event.objects.last()
        self.assertLessEqual(event.date.second - timezone.now().second, 2)
        self.assertEqual(event.game, game)
        self.assertEqual(event.message, "The game ended.")


class CreateTaleViewTest(TestCase):
    path_name = "tale-create"

    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="add_tale")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()

        game = gmodels.Game.objects.create()
        gmodels.Character.objects.create(game=game, name=utils.generate_random_name(5))
        gmodels.Character.objects.create(game=game, name=utils.generate_random_name(5))
        game.start()
        game.save()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def tearDown(self):
        cache.clear()

    def test_view_mapping(self):
        game = gmodels.Game.objects.last()
        response = self.client.get(reverse(self.path_name, args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, gvmaster.CreateTaleView
        )

    def test_template_mapping(self):
        game = gmodels.Game.objects.last()
        response = self.client.get(reverse(self.path_name, args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/createtale.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse(self.path_name, args=[game_id]))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_context_data(self):
        game = gmodels.Game.objects.last()
        response = self.client.get(reverse(self.path_name, args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], game)

    def test_game_is_under_preparation(self):
        game = gmodels.Game.objects.create()
        response = self.client.get(reverse(self.path_name, args=[game.id]))
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_game_is_finished(self):
        game = gmodels.Game.objects.last()
        game.end()
        game.save()
        response = self.client.get(reverse(self.path_name, args=[game.id]))
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_tale_creation(self):
        content = utils.generate_random_string(100)
        data = {"content": f"{content}"}
        form = gforms.CreateTaleForm(data)
        self.assertTrue(form.is_valid())
        game = gmodels.Game.objects.last()

        response = self.client.post(
            reverse(self.path_name, args=[game.id]), data=form.cleaned_data
        )
        self.assertEqual(response.status_code, 302)
        tale = gmodels.Tale.objects.last()
        self.assertEqual(tale.game, game)
        self.assertEqual(tale.message, "The Master updated the story.")
        self.assertEqual(tale.content, form.cleaned_data["content"])
        self.assertRedirects(response, reverse("game", args=[game.id]))


class CreatePendingActionViewTest(TestCase):
    path_name = "pendingaction-create"

    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="add_pendingaction")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()

        game = gmodels.Game.objects.create()
        gmodels.Character.objects.create(game=game, name=utils.generate_random_name(5))
        gmodels.Character.objects.create(game=game, name=utils.generate_random_name(5))
        game.start()
        game.save()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def tearDown(self):
        cache.clear()

    def test_view_mapping(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, gvmaster.CreatePendingActionView
        )

    def test_template_mapping(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/creatependingaction.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game_id, character.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_character_not_exists(self):
        game = gmodels.Game.objects.last()
        character_id = random.randint(10000, 99999)
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character_id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_context_data(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], game)
        self.assertEqual(response.context["character"], character)

    def test_game_is_under_preparation(self):
        game = gmodels.Game.objects.create()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_game_is_finished(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        game.end()
        game.save()

        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_pending_action_creation_ok(self):
        action_type = random.choice(gmodels.PendingAction.ACTION_TYPES)
        data = {"action_type": f"{action_type[0]}"}
        form = gforms.CreatePendingActionForm(data)
        self.assertTrue(form.is_valid())
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()

        response = self.client.post(
            reverse(self.path_name, args=[game.id, character.id]),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        pending_action = gmodels.PendingAction.objects.last()
        self.assertEqual(pending_action.game, game)
        self.assertLessEqual(pending_action.date.second - timezone.now().second, 2)
        self.assertEqual(
            pending_action.message,
            f"{character} needs to perform an action: {pending_action.get_action_type_display()}",
        )
        self.assertEqual(pending_action.action_type, form.cleaned_data["action_type"])
        self.assertRedirects(response, reverse("game", args=[game.id]))

    def test_pending_action_creation_ko_character_has_pending_actions(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        gmodels.PendingAction.objects.create(game=game, character=character)
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id]),
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)


class IncreaseXpViewTest(TestCase):
    path_name = "xpincrease-create"

    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="add_xpincrease")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()

        game = gmodels.Game.objects.create()
        gmodels.Character.objects.create(game=game, name=utils.generate_random_name(5))
        gmodels.Character.objects.create(game=game, name=utils.generate_random_name(5))
        game.start()
        game.save()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def tearDown(self):
        cache.clear()

    def test_view_mapping(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, gvmaster.IncreaseXpView
        )

    def test_template_mapping(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/xp.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game_id, character.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_character_not_exists(self):
        game = gmodels.Game.objects.last()
        character_id = random.randint(10000, 99999)
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character_id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_context_data(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], game)
        self.assertEqual(response.context["character"], character)

    def test_game_is_under_preparation(self):
        game = gmodels.Game.objects.create()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_game_is_finished(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        game.end()
        game.save()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_creation_ok(self):
        xp = random.randint(1, 20)
        data = {"xp": f"{xp}"}
        form = gforms.IncreaseXpForm(data)
        self.assertTrue(form.is_valid())
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()

        response = self.client.post(
            reverse(self.path_name, args=[game.id, character.id]),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        xp_increase = gmodels.XpIncrease.objects.last()
        self.assertEqual(xp_increase.game, game)
        self.assertEqual(xp_increase.character, character)
        self.assertLessEqual(xp_increase.date.second - timezone.now().second, 2)
        self.assertEqual(
            xp_increase.message,
            f"{character} gained experience: +{xp_increase.xp} XP!",
        )
        self.assertEqual(xp_increase.xp, form.cleaned_data["xp"])
        self.assertRedirects(response, reverse("game", args=[game.id]))

    def test_creation_ko_invalid_form(self):
        xp = random.randint(-20, 0)
        data = {"xp": f"{xp}"}
        form = gforms.IncreaseXpForm(data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)


class DamageViewTest(TestCase):
    path_name = "damage-create"

    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="add_damage")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()

        game = gmodels.Game.objects.create()
        gmodels.Character.objects.create(game=game, name=utils.generate_random_name(5))
        gmodels.Character.objects.create(game=game, name=utils.generate_random_name(5))
        game.start()
        game.save()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def tearDown(self):
        cache.clear()

    def test_view_mapping(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, gvmaster.DamageView)

    def test_template_mapping(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/damage.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game_id, character.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_character_not_exists(self):
        game = gmodels.Game.objects.last()
        character_id = random.randint(10000, 99999)
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character_id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_context_data(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], game)
        self.assertEqual(response.context["character"], character)

    def test_game_is_under_preparation(self):
        game = gmodels.Game.objects.create()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_game_is_finished(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        game.end()
        game.save()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_creation_ok(self):
        hp = random.randint(1, 20)
        data = {"hp": f"{hp}"}
        form = gforms.DamageForm(data)
        self.assertTrue(form.is_valid())
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()

        response = self.client.post(
            reverse(self.path_name, args=[game.id, character.id]),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        damage = gmodels.Damage.objects.last()
        self.assertEqual(damage.game, game)
        self.assertEqual(damage.character, character)
        self.assertLessEqual(damage.date.second - timezone.now().second, 2)
        self.assertEqual(
            damage.message,
            f"{character} was hit: -{damage.hp} HP!",
        )
        self.assertEqual(damage.hp, form.cleaned_data["hp"])
        self.assertRedirects(response, reverse("game", args=[game.id]))

    def test_creation_ko_invalid_form(self):
        hp = random.randint(-20, 0)
        data = {"hp": f"{hp}"}
        form = gforms.DamageForm(data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)

    def test_death(self):
        hp = 1000
        data = {"hp": f"{hp}"}
        form = gforms.DamageForm(data)
        self.assertTrue(form.is_valid())
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()

        response = self.client.post(
            reverse(self.path_name, args=[game.id, character.id]),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        damage = gmodels.Damage.objects.last()
        self.assertEqual(damage.game, game)
        self.assertEqual(damage.character, character)
        self.assertLessEqual(damage.date.second - timezone.now().second, 2)
        self.assertEqual(
            damage.message,
            f"{character} was hit: -{damage.hp} HP! {character} is dead.",
        )
        self.assertEqual(damage.hp, form.cleaned_data["hp"])
        character = gmodels.Character.objects.last()
        self.assertIsNone(character.game)
        self.assertEqual(character.hp, character.max_hp)
        self.assertRedirects(response, reverse("game", args=[game.id]))


class HealViewTest(TestCase):
    path_name = "healing-create"

    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="add_healing")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()

        game = gmodels.Game.objects.create()
        gmodels.Character.objects.create(
            game=game, name=utils.generate_random_name(5), hp=1
        )
        gmodels.Character.objects.create(
            game=game, name=utils.generate_random_name(5), hp=1
        )
        game.start()
        game.save()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def tearDown(self):
        cache.clear()

    def test_view_mapping(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, gvmaster.HealView)

    def test_template_mapping(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/heal.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game_id, character.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_character_not_exists(self):
        game = gmodels.Game.objects.last()
        character_id = random.randint(10000, 99999)
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character_id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_context_data(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], game)
        self.assertEqual(response.context["character"], character)

    def test_game_is_under_preparation(self):
        game = gmodels.Game.objects.create()
        character = gmodels.Character.objects.last()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_game_is_finished(self):
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()
        game.end()
        game.save()
        response = self.client.get(
            reverse(self.path_name, args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_creation_ok(self):
        hp = random.randint(1, 20)
        data = {"hp": f"{hp}"}
        form = gforms.HealForm(data)
        self.assertTrue(form.is_valid())
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()

        response = self.client.post(
            reverse(self.path_name, args=[game.id, character.id]),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        healing = gmodels.Healing.objects.last()
        self.assertEqual(healing.game, game)
        self.assertEqual(healing.character, character)
        self.assertLessEqual(healing.date.second - timezone.now().second, 2)
        self.assertEqual(
            healing.message,
            f"{character} was healed: +{healing.hp} HP!",
        )
        self.assertEqual(healing.hp, form.cleaned_data["hp"])
        self.assertRedirects(response, reverse("game", args=[game.id]))

    def test_creation_ko_invalid_form(self):
        hp = random.randint(-20, 0)
        data = {"hp": f"{hp}"}
        form = gforms.HealForm(data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)

    def test_healing_not_exceed_character_max_hp(self):
        hp = 1000
        data = {"hp": f"{hp}"}
        form = gforms.HealForm(data)
        self.assertTrue(form.is_valid())
        game = gmodels.Game.objects.last()
        character = gmodels.Character.objects.last()

        response = self.client.post(
            reverse(self.path_name, args=[game.id, character.id]),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        healing = gmodels.Healing.objects.last()
        self.assertEqual(healing.game, game)
        self.assertEqual(healing.character, character)
        self.assertLessEqual(healing.date.second - timezone.now().second, 2)
        self.assertEqual(
            healing.message,
            f"{character} was healed: +{healing.hp} HP!",
        )
        self.assertEqual(healing.hp, character.max_hp - character.hp)
        self.assertRedirects(response, reverse("game", args=[game.id]))
