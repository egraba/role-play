import random

from django.db import models
from django.test import TestCase
from django.utils import timezone

import character.models as cmodels
import game.models as gmodels
import utils.testing.random as utrandom


class GameModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        gmodels.Game.objects.create(name=utrandom.ascii_letters_string(50))

    def setUp(self):
        self.game = gmodels.Game.objects.last()

    def test_name_type(self):
        name = self.game._meta.get_field("name")
        self.assertTrue(name, models.CharField)

    def test_name_max_length(self):
        max_length = self.game._meta.get_field("name").max_length
        self.assertEqual(max_length, 50)

    def test_start_date_type(self):
        start_date = self.game._meta.get_field("start_date")
        self.assertTrue(start_date, models.DateTimeField)

    def test_end_date_type(self):
        end_date = self.game._meta.get_field("end_date")
        self.assertTrue(end_date, models.DateTimeField)

    def test_end_date_default_value(self):
        self.assertEqual(self.game.end_date, None)

    def test_status_type(self):
        status = self.game._meta.get_field("status")
        self.assertTrue(status, models.CharField)

    def test_str_is_name(self):
        self.assertEqual(str(self.game), self.game.name)

    def test_is_ongoing(self):
        self.assertFalse(self.game.is_ongoing())
        number_of_players = 5
        for i in range(number_of_players):
            gmodels.Player.objects.create(
                game=self.game,
                character=cmodels.Character.objects.create(
                    name=utrandom.ascii_letters_string(5)
                ),
            )
        self.game.start()
        self.game.save()
        self.assertTrue(self.game.is_ongoing())
        self.game.end()
        self.game.save()
        self.assertFalse(self.game.is_ongoing())


class EventModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = gmodels.Game.objects.create()
        gmodels.Event.objects.create(game=game)

    def test_game_type(self):
        event = gmodels.Event.objects.last()
        game = event._meta.get_field("game")
        self.assertTrue(game, models.ForeignKey)

    def test_date_type(self):
        event = gmodels.Event.objects.last()
        date = event._meta.get_field("date")
        self.assertTrue(date, models.DateTimeField)

    def test_date_default_value(self):
        event = gmodels.Event.objects.last()
        self.assertEqual(event.date.second, timezone.now().second)

    def test_message_type(self):
        event = gmodels.Event.objects.last()
        message = event._meta.get_field("message")
        self.assertTrue(message, models.CharField)

    def test_message_max_length(self):
        event = gmodels.Event.objects.last()
        max_length = event._meta.get_field("message").max_length
        self.assertEqual(max_length, 100)

    def test_str(self):
        event = gmodels.Event.objects.last()
        self.assertEqual(str(event), event.message)


class TaleModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = gmodels.Game.objects.create()
        gmodels.Tale.objects.create(game=game)

    def test_content_type(self):
        tale = gmodels.Tale.objects.last()
        content = tale._meta.get_field("content")
        self.assertTrue(content, models.CharField)

    def test_content_max_length(self):
        tale = gmodels.Tale.objects.last()
        max_length = tale._meta.get_field("content").max_length
        self.assertEqual(max_length, 1000)

    def test_str(self):
        tale = gmodels.Tale.objects.last()
        self.assertEqual(str(tale), tale.content)


class PendingActionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = gmodels.Game.objects.create()
        character = cmodels.Character.objects.get_or_create(id=1)[0]
        gmodels.PendingAction.objects.create(game=game, character=character)

    def test_character_type(self):
        pending_action = gmodels.PendingAction.objects.last()
        character = pending_action._meta.get_field("character")
        self.assertTrue(character, models.OneToOneField)

    def test_action_type_type(self):
        pending_action = gmodels.PendingAction.objects.last()
        action_type = pending_action._meta.get_field("action_type")
        self.assertTrue(action_type, models.CharField)

    def test_action_type_max_length(self):
        pending_action = gmodels.PendingAction.objects.last()
        max_length = pending_action._meta.get_field("action_type").max_length
        self.assertEqual(max_length, 1)

    def test_str(self):
        pending_action = gmodels.PendingAction.objects.last()
        self.assertEqual(str(pending_action), pending_action.action_type)


class XpIncreaseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = gmodels.Game.objects.create()
        character = cmodels.Character.objects.create()
        gmodels.XpIncrease.objects.create(
            game=game, character=character, xp=random.randint(1, 20)
        )

    def test_hp_type(self):
        xp_increase = gmodels.XpIncrease.objects.last()
        xp = xp_increase._meta.get_field("xp")
        self.assertTrue(xp, models.SmallIntegerField)

    def test_str(self):
        xp_increase = gmodels.XpIncrease.objects.last()
        self.assertEqual(str(xp_increase), str(xp_increase.xp))


class DamageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = gmodels.Game.objects.create()
        character = cmodels.Character.objects.create()
        gmodels.Damage.objects.create(
            game=game, character=character, hp=random.randint(1, 20)
        )

    def test_hp_type(self):
        damage = gmodels.Damage.objects.last()
        hp = damage._meta.get_field("hp")
        self.assertTrue(hp, models.SmallIntegerField)

    def test_str(self):
        damage = gmodels.Damage.objects.last()
        self.assertEqual(str(damage), str(damage.hp))


class HealingModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = gmodels.Game.objects.create()
        character = cmodels.Character.objects.create()
        gmodels.Healing.objects.create(
            game=game, character=character, hp=random.randint(1, 20)
        )

    def test_hp_type(self):
        healing = gmodels.Healing.objects.last()
        hp = healing._meta.get_field("hp")
        self.assertTrue(hp, models.SmallIntegerField)

    def test_str(self):
        healing = gmodels.Healing.objects.last()
        self.assertEqual(str(healing), str(healing.hp))


class DiceLaunchModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = gmodels.Game.objects.create()
        character = cmodels.Character.objects.create()
        gmodels.DiceLaunch.objects.create(
            game=game, character=character, score=random.randint(1, 20)
        )

    def test_character_type(self):
        dice_launch = gmodels.DiceLaunch.objects.last()
        character = dice_launch._meta.get_field("character")
        self.assertTrue(character, models.ForeignKey)

    def test_score_type(self):
        dice_launch = gmodels.DiceLaunch.objects.last()
        score = dice_launch._meta.get_field("score")
        self.assertTrue(score, models.SmallIntegerField)

    def test_str(self):
        dice_launch = gmodels.DiceLaunch.objects.last()
        self.assertEqual(str(dice_launch), str(dice_launch.score))


class ChoiceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = gmodels.Game.objects.create()
        character = cmodels.Character.objects.create()
        gmodels.Choice.objects.create(
            game=game, character=character, selection=utrandom.printable_string(50)
        )

    def setUp(self):
        self.choice = gmodels.Choice.objects.last()

    def test_character_type(self):
        character = self.choice._meta.get_field("character")
        self.assertTrue(character, models.ForeignKey)

    def test_selection_type(self):
        selection = self.choice._meta.get_field("selection")
        self.assertTrue(selection, models.SmallIntegerField)

    def test_selection_max_length(self):
        max_length = self.choice._meta.get_field("selection").max_length
        self.assertEqual(max_length, 50)

    def test_str(self):
        self.assertEqual(str(self.choice), self.choice.selection)
