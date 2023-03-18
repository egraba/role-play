import random

from django.contrib.auth.models import Permission, User
from django.core.exceptions import PermissionDenied
from django.forms import ValidationError
from django.http import Http404
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from game.forms import (
    CreateGameForm,
    CreatePendingActionForm,
    CreateTaleForm,
    DamageForm,
    IncreaseXpForm,
)
from game.models import Character, Damage, Game, PendingAction, Tale, XpIncrease
from game.tests import utils
from game.views.master import (
    AddCharacterView,
    CreateGameView,
    CreatePendingActionView,
    CreateTaleView,
    DamageView,
    EndGameView,
    IncreaseXpView,
    StartGameView,
)


class CreateGameViewTest(TestCase):
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
        response = self.client.get(reverse("game-create"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, CreateGameView)

    def test_template_mapping(self):
        response = self.client.get(reverse("game-create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/creategame.html")

    def test_game_creation(self):
        name = utils.generate_random_name(20)
        description = utils.generate_random_string(100)
        data = {"name": f"{name}", "description": f"{description}"}
        form = CreateGameForm(data)
        self.assertTrue(form.is_valid())
        response = self.client.post(reverse("game-create"), data=form.cleaned_data)
        self.assertEqual(response.status_code, 302)
        game = Game.objects.last()
        self.assertEqual(game.name, name)
        self.assertEqual(game.status, "P")
        tale = Tale.objects.last()
        self.assertEqual(tale.game, game)
        self.assertEqual(tale.message, "The Master created the story.")
        self.assertEqual(tale.description, form.cleaned_data["description"])
        self.assertRedirects(response, reverse("index"))


class AddCharacterViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="change_character")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()
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

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-add-character", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, AddCharacterView)

    def test_template_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-add-character", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/addcharacter.html")

    def test_pagination_size(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-add-character", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["character_list"]), 10)

    def test_pagination_size_next_page(self):
        game = Game.objects.last()
        response = self.client.get(
            reverse("game-add-character", args=[game.id]) + "?page=2"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["character_list"]), 2)

    def test_ordering(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-add-character", args=[game.id]))
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
        response = self.client.get(reverse("game-add-character", args=[game_id]))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)


class StartGameViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="change_game")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()
        Game.objects.create()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-start", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, StartGameView)

    def test_template_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-start", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/startgame.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse("game-start", args=[game_id]))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_game_start_ok(self):
        game = Game.objects.last()
        number_of_characters = 2
        for i in range(number_of_characters):
            Character.objects.create(game=game, name=utils.generate_random_name(5))
        response = self.client.post(reverse("game-start", args=[game.id]))
        self.assertEqual(response.status_code, 302)
        game = Game.objects.last()
        self.assertEqual(game.status, "O")

    def test_game_start_not_enough_characters(self):
        game = Game.objects.last()
        number_of_characters = 1
        for i in range(number_of_characters):
            Character.objects.create(game=game, name=utils.generate_random_name(5))
        response = self.client.post(reverse("game-start", args=[game.id]))
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)
        game = Game.objects.last()
        self.assertEqual(game.status, "P")


class EndGameViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="change_game")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()
        Game.objects.create()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-end", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, EndGameView)

    def test_template_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("game-end", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/endgame.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse("game-end", args=[game_id]))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_game_end_ok(self):
        game = Game.objects.last()
        number_of_characters = 5
        for i in range(number_of_characters):
            Character.objects.create(game=game, name=utils.generate_random_name(5))
        game.start()
        game.save()
        response = self.client.post(reverse("game-end", args=[game.id]))
        self.assertEqual(response.status_code, 302)
        game = Game.objects.last()
        self.assertEqual(game.status, "F")
        self.assertTrue(Character.objects.filter(game=game).count() == 0)


class CreateTaleViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="add_tale")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()
        Game.objects.create()

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("tale-create", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, CreateTaleView)

    def test_template_mapping(self):
        game = Game.objects.last()
        response = self.client.get(reverse("tale-create", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/createtale.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse("tale-create", args=[game_id]))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_context_data(self):
        game = Game.objects.last()
        response = self.client.get(reverse("tale-create", args=[game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.context["game"], game)

    def test_tale_creation(self):
        description = utils.generate_random_string(100)
        data = {"description": f"{description}"}
        form = CreateTaleForm(data)
        self.assertTrue(form.is_valid())
        game = Game.objects.last()
        response = self.client.post(
            reverse("tale-create", args=[game.id]), data=form.cleaned_data
        )
        self.assertEqual(response.status_code, 302)
        tale = Tale.objects.last()
        self.assertEqual(tale.game, game)
        self.assertEqual(tale.message, "The Master updated the story.")
        self.assertEqual(tale.description, form.cleaned_data["description"])
        self.assertRedirects(response, reverse("game", args=[game.id]))


class CreatePendingActionViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="add_pendingaction")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()
        game = Game.objects.create()
        Character.objects.create(game=game)

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(
            reverse("character-add-pending-action", args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, CreatePendingActionView
        )

    def test_template_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(
            reverse("character-add-pending-action", args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/creatependingaction.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        character = Character.objects.last()
        response = self.client.get(
            reverse("character-add-pending-action", args=[game_id, character.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_context_data(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(
            reverse("character-add-pending-action", args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.context["game"], game)

    def test_pending_action_creation_ok(self):
        action_type = random.choice(PendingAction.ACTION_TYPES)
        data = {"action_type": f"{action_type[0]}"}
        form = CreatePendingActionForm(data)
        self.assertTrue(form.is_valid())
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.post(
            reverse("character-add-pending-action", args=[game.id, character.id]),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        pending_action = PendingAction.objects.last()
        self.assertEqual(pending_action.game, game)
        self.assertEqual(pending_action.date.second, timezone.now().second)
        self.assertEqual(
            pending_action.message,
            f"{character} needs to perform an action: {pending_action.get_action_type_display()}",
        )
        self.assertEqual(pending_action.action_type, form.cleaned_data["action_type"])
        self.assertRedirects(response, reverse("game", args=[game.id]))

    def test_pending_action_creation_ko_character_has_pending_actions(self):
        game = Game.objects.last()
        character = Character.objects.last()
        PendingAction.objects.create(game=game, character=character)
        response = self.client.get(
            reverse("character-add-pending-action", args=[game.id, character.id]),
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)


class IncreaseXpViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="add_xpincrease")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()
        game = Game.objects.create()
        Character.objects.create(game=game)

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(
            reverse("character-increase-xp", args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, IncreaseXpView)

    def test_template_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(
            reverse("character-increase-xp", args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/xp.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        character = Character.objects.last()
        response = self.client.get(
            reverse("character-increase-xp", args=[game_id, character.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_context_data(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(
            reverse("character-increase-xp", args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.context["game"], game)
        self.assertEquals(response.context["character"], character)

    def test_creation_ok(self):
        xp = random.randint(1, 20)
        data = {"xp": f"{xp}"}
        form = IncreaseXpForm(data)
        self.assertTrue(form.is_valid())
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.post(
            reverse("character-increase-xp", args=[game.id, character.id]),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        xp_increase = XpIncrease.objects.last()
        self.assertEqual(xp_increase.game, game)
        self.assertEqual(xp_increase.character, character)
        self.assertEqual(xp_increase.date.second, timezone.now().second)
        self.assertEqual(
            xp_increase.message,
            f"{character} gained experience: +{xp_increase.xp} XP!",
        )
        self.assertEqual(xp_increase.xp, form.cleaned_data["xp"])
        self.assertRedirects(response, reverse("game", args=[game.id]))

    def test_creation_ko_invalid_form(self):
        xp = random.randint(-20, 0)
        data = {"xp": f"{xp}"}
        form = IncreaseXpForm(data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)


class DamageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        permission = Permission.objects.get(codename="add_damage")
        user = User.objects.create(username=utils.generate_random_name(5))
        user.set_password("pwd")
        user.user_permissions.add(permission)
        user.save()
        game = Game.objects.create()
        Character.objects.create(game=game)

    def setUp(self):
        self.user = User.objects.last()
        self.client.login(username=self.user.username, password="pwd")

    def test_view_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(
            reverse("character-damage", args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, DamageView)

    def test_template_mapping(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(
            reverse("character-damage", args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/damage.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        character = Character.objects.last()
        response = self.client.get(
            reverse("character-damage", args=[game_id, character.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_context_data(self):
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.get(
            reverse("character-damage", args=[game.id, character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.context["game"], game)
        self.assertEquals(response.context["character"], character)

    def test_creation_ok(self):
        hp = random.randint(1, 20)
        data = {"hp": f"{hp}"}
        form = DamageForm(data)
        self.assertTrue(form.is_valid())
        game = Game.objects.last()
        character = Character.objects.last()
        response = self.client.post(
            reverse("character-damage", args=[game.id, character.id]),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        damage = Damage.objects.last()
        self.assertEqual(damage.game, game)
        self.assertEqual(damage.character, character)
        self.assertEqual(damage.date.second, timezone.now().second)
        self.assertEqual(
            damage.message,
            f"{character} was hit: -{damage.hp} HP!",
        )
        self.assertEqual(damage.hp, form.cleaned_data["hp"])
        self.assertRedirects(response, reverse("game", args=[game.id]))

    def test_creation_ko_invalid_form(self):
        hp = random.randint(-20, 0)
        data = {"hp": f"{hp}"}
        form = DamageForm(data)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)
