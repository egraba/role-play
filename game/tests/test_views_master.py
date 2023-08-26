import random

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.forms import ValidationError
from django.http import Http404
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from faker import Faker

import character.models as cmodels
import game.forms as gforms
import game.models as gmodels
import game.views.master as gvmaster
import utils.testing.factories as utfactories


class CharacterInviteViewTest(TestCase):
    path_name = "game-invite-character"

    @classmethod
    def setUpTestData(cls):
        game = utfactories.GameFactory(master__user__username="master")
        number_of_characters_in_a_game = 5
        number_of_characters_not_in_a_game = 12
        for i in range(number_of_characters_in_a_game):
            utfactories.PlayerFactory(game=game)
        for i in range(number_of_characters_not_in_a_game):
            utfactories.CharacterFactory()

    def setUp(self):
        self.user = User.objects.get(username="master")
        self.client.login(username=self.user.username, password="pwd")
        self.game = gmodels.Game.objects.last()

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name, args=(self.game.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, gvmaster.CharacterInviteView
        )

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name, args=(self.game.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/character_invite.html")

    def test_pagination_size(self):
        response = self.client.get(reverse(self.path_name, args=(self.game.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["character_list"]), 10)

    def test_pagination_size_next_page(self):
        response = self.client.get(
            reverse(self.path_name, args=(self.game.id,)) + "?page=2"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["character_list"]), 2)

    def test_ordering(self):
        response = self.client.get(reverse(self.path_name, args=(self.game.id,)))
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
        response = self.client.get(reverse(self.path_name, args=(game_id,)))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_context_data(self):
        character_list = cmodels.Character.objects.filter(player__game=None)
        response = self.client.get(reverse(self.path_name, args=(self.game.id,)))
        self.assertTrue(
            set(response.context["character_list"]).issubset(character_list)
        )

    def test_context_data_all_characters_already_assigned(self):
        cmodels.Character.objects.filter(player=None).delete()
        response = self.client.get(reverse(self.path_name, args=(self.game.id,)))
        self.assertFalse(response.context["character_list"])


class CharacterInviteConfirmViewTest(TestCase):
    path_name = "game-invite-character-confirm"

    @classmethod
    def setUpTestData(cls):
        game = utfactories.GameFactory(master__user__username="master")
        utfactories.PlayerFactory(game=game)

    def setUp(self):
        self.user = User.objects.get(username="master")
        self.client.login(username=self.user.username, password="pwd")
        self.game = gmodels.Game.objects.last()
        self.character = cmodels.Character.objects.get(player__game=self.game)

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
            response.resolver_match.func.view_class, gvmaster.CharacterInviteConfirmView
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
        self.assertTemplateUsed(response, "game/character_invite_confirm.html")

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

    def test_character_added_to_game(self):
        character = utfactories.CharacterFactory()
        response = self.client.post(
            reverse(
                self.path_name,
                args=(
                    self.game.id,
                    character.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("game", args=(self.game.id,)))
        self.assertEqual(self.character.player.game, self.game)
        event = gmodels.Event.objects.last()
        self.assertLessEqual(event.date.second - timezone.now().second, 2)
        self.assertEqual(event.game, self.game)
        self.assertEqual(event.message, f"{character} was added to the game.")


class GameStartViewTest(TestCase):
    path_name = "game-start"

    @classmethod
    def setUpTestData(cls):
        utfactories.GameFactory(master__user__username="master")

    def setUp(self):
        self.user = User.objects.get(username="master")
        self.client.login(username=self.user.username, password="pwd")
        self.game = gmodels.Game.objects.last()

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name, args=(self.game.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, gvmaster.GameStartView
        )

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name, args=(self.game.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/game_start.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse(self.path_name, args=(game_id,)))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_game_start_ok(self):
        number_of_players = 2
        for _ in range(number_of_players):
            utfactories.PlayerFactory(game=self.game)
        response = self.client.post(reverse(self.path_name, args=(self.game.id,)))
        self.assertEqual(response.status_code, 302)
        # Need to query the game again.
        self.game = gmodels.Game.objects.last()
        self.assertTrue(self.game.is_ongoing())
        self.assertLessEqual(self.game.start_date.second - timezone.now().second, 2)
        event = gmodels.Event.objects.last()
        self.assertLessEqual(event.date.second - timezone.now().second, 2)
        self.assertEqual(event.game, self.game)
        self.assertEqual(event.message, "the game started.")

    def test_game_start_not_enough_characters(self):
        utfactories.PlayerFactory(game=self.game)
        response = self.client.post(reverse(self.path_name, args=(self.game.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertRaises(PermissionDenied)
        self.assertTrue(self.game.is_under_preparation())
        self.assertRedirects(
            response, reverse("game-start-error", args=(self.game.id,))
        )


class TaleCreateViewTest(TestCase):
    path_name = "tale-create"

    @classmethod
    def setUpTestData(cls):
        game = utfactories.GameFactory(master__user__username="master")
        number_of_players = 3
        for _ in range(number_of_players):
            utfactories.PlayerFactory(game=game)
        game.start()
        game.save()

    def setUp(self):
        self.user = User.objects.get(username="master")
        self.client.login(username=self.user.username, password="pwd")
        self.game = gmodels.Game.objects.last()
        self.character = cmodels.Character.objects.last()

    def tearDown(self):
        cache.clear()

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name, args=(self.game.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.func.view_class, gvmaster.TaleCreateView
        )

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name, args=(self.game.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/tale_create.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(reverse(self.path_name, args=(game_id,)))
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_context_data(self):
        response = self.client.get(reverse(self.path_name, args=(self.game.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], self.game)

    def test_game_is_under_preparation(self):
        self.game.status = "P"
        self.game.save()
        response = self.client.get(reverse(self.path_name, args=(self.game.id,)))
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_tale_creation(self):
        fake = Faker()
        content = fake.text(100)
        data = {"content": f"{content}"}
        form = gforms.CreateTaleForm(data)
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(self.path_name, args=(self.game.id,)), data=form.cleaned_data
        )
        self.assertEqual(response.status_code, 302)
        tale = gmodels.Tale.objects.filter(game=self.game).last()
        self.assertEqual(tale.game, self.game)
        self.assertEqual(tale.message, "the Master updated the story.")
        self.assertEqual(tale.content, form.cleaned_data["content"])
        self.assertRedirects(response, self.game.get_absolute_url())


class XpIncreaseViewTest(TestCase):
    path_name = "xpincrease-create"

    @classmethod
    def setUpTestData(cls):
        game = utfactories.GameFactory(master__user__username="master")
        number_of_players = 3
        for _ in range(number_of_players):
            utfactories.PlayerFactory(game=game)
        game.start()
        game.save()

    def setUp(self):
        self.user = User.objects.get(username="master")
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
            response.resolver_match.func.view_class, gvmaster.XpIncreaseView
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
        self.assertTemplateUsed(response, "game/xp.html")

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

    def test_creation_ok(self):
        xp = random.randint(1, 20)
        data = {"xp": f"{xp}"}
        form = gforms.IncreaseXpForm(data)
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
        xp_increase = gmodels.XpIncrease.objects.last()
        self.assertEqual(xp_increase.game, self.game)
        self.assertEqual(xp_increase.character, self.character)
        self.assertLessEqual(xp_increase.date.second - timezone.now().second, 2)
        self.assertEqual(
            xp_increase.message,
            f"{self.character} gained experience: +{xp_increase.xp} XP!",
        )
        self.assertEqual(xp_increase.xp, form.cleaned_data["xp"])
        self.assertRedirects(response, self.game.get_absolute_url())

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
        game = utfactories.GameFactory(master__user__username="master")
        number_of_players = 3
        for _ in range(number_of_players):
            utfactories.PlayerFactory(game=game)
        game.start()
        game.save()

    def setUp(self):
        self.user = User.objects.get(username="master")
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
        self.assertEqual(response.resolver_match.func.view_class, gvmaster.DamageView)

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
        self.assertTemplateUsed(response, "game/damage.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(
            reverse(self.path_name, args=[game_id, self.character.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_character_not_exists(self):
        character_id = random.randint(10000, 99999)
        response = self.client.get(
            reverse(self.path_name, args=[self.game.id, character_id])
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

    def test_creation_ok(self):
        hp = random.randint(1, 20)
        data = {"hp": f"{hp}"}
        form = gforms.DamageForm(data)
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
        damage = gmodels.Damage.objects.last()
        self.assertEqual(damage.game, self.game)
        self.assertEqual(damage.character, self.character)
        self.assertLessEqual(damage.date.second - timezone.now().second, 2)
        self.assertEqual(
            damage.message,
            f"{self.character} was hit: -{damage.hp} HP!",
        )
        self.assertEqual(damage.hp, form.cleaned_data["hp"])
        self.assertRedirects(response, self.game.get_absolute_url())

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
        damage = gmodels.Damage.objects.last()
        self.assertEqual(damage.game, self.game)
        self.assertEqual(damage.character, self.character)
        self.assertLessEqual(damage.date.second - timezone.now().second, 2)
        self.assertEqual(
            damage.message,
            f"{self.character} was hit: -{damage.hp} HP! {self.character} is dead.",
        )
        self.assertEqual(damage.hp, form.cleaned_data["hp"])
        self.assertFalse(hasattr(self.character, "player"))
        self.assertEqual(self.character.hp, self.character.max_hp)
        self.assertRedirects(response, self.game.get_absolute_url())


class HealViewTest(TestCase):
    path_name = "healing-create"

    @classmethod
    def setUpTestData(cls):
        game = utfactories.GameFactory(master__user__username="master")
        number_of_players = 3
        for _ in range(number_of_players):
            utfactories.PlayerFactory(game=game)
        game.start()
        game.save()

    def setUp(self):
        self.user = User.objects.get(username="master")
        self.client.login(username=self.user.username, password="pwd")
        self.game = gmodels.Game.objects.last()
        self.character = cmodels.Character.objects.last()
        # The character needs to have low HP, in order to be healed.
        self.character.hp = 1
        self.character.save()

    def tearDown(self):
        cache.clear()

    def test_view_mapping(self):
        response = self.client.get(
            reverse(self.path_name, args=[self.game.id, self.character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, gvmaster.HealingView)

    def test_template_mapping(self):
        response = self.client.get(
            reverse(self.path_name, args=[self.game.id, self.character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/heal.html")

    def test_game_not_exists(self):
        game_id = random.randint(10000, 99999)
        response = self.client.get(
            reverse(self.path_name, args=[game_id, self.character.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_character_not_exists(self):
        character_id = random.randint(10000, 99999)
        response = self.client.get(
            reverse(self.path_name, args=[self.game.id, character_id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertRaises(Http404)

    def test_context_data(self):
        response = self.client.get(
            reverse(self.path_name, args=[self.game.id, self.character.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["game"], self.game)
        self.assertEqual(response.context["character"], self.character)

    def test_game_is_under_preparation(self):
        self.game.status = "P"
        self.game.save()
        response = self.client.get(
            reverse(self.path_name, args=[self.game.id, self.character.id])
        )
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionDenied)

    def test_creation_ok(self):
        hp = random.randint(1, 20)
        data = {"hp": f"{hp}"}
        form = gforms.HealForm(data)
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(self.path_name, args=[self.game.id, self.character.id]),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        healing = gmodels.Healing.objects.last()
        self.assertEqual(healing.game, self.game)
        self.assertEqual(healing.character, self.character)
        self.assertLessEqual(healing.date.second - timezone.now().second, 2)
        self.assertEqual(
            healing.message,
            f"{self.character} was healed: +{healing.hp} HP!",
        )
        self.assertEqual(healing.hp, form.cleaned_data["hp"])
        self.assertRedirects(response, self.game.get_absolute_url())

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

        response = self.client.post(
            reverse(self.path_name, args=[self.game.id, self.character.id]),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        healing = gmodels.Healing.objects.last()
        self.assertEqual(healing.game, self.game)
        self.assertEqual(healing.character, self.character)
        self.assertLessEqual(healing.date.second - timezone.now().second, 2)
        self.assertEqual(
            healing.message,
            f"{self.character} was healed: +{healing.hp} HP!",
        )
        self.assertEqual(healing.hp, self.character.max_hp - self.character.hp)
        self.assertRedirects(response, self.game.get_absolute_url())
