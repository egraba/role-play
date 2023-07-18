import random

from django.contrib.auth.models import User
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

    def test_story_type(self):
        story = self.game._meta.get_field("story")
        self.assertTrue(story, models.ForeignKey)

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

    def test_status_methods(self):
        self.assertTrue(self.game.is_under_preparation())
        self.assertFalse(self.game.is_ongoing())
        self.assertFalse(self.game.is_finished())
        number_of_players = 5
        for i in range(number_of_players):
            user = User.objects.create(username=utrandom.ascii_letters_string(7))
            gmodels.Player.objects.create(
                user=user,
                game=self.game,
                character=cmodels.Character.objects.create(
                    name=utrandom.ascii_letters_string(5)
                ),
            )
        self.game.start()
        self.game.save()
        self.assertFalse(self.game.is_under_preparation())
        self.assertTrue(self.game.is_ongoing())
        self.assertFalse(self.game.is_finished())
        self.game.end()
        self.game.save()
        self.assertFalse(self.game.is_under_preparation())
        self.assertFalse(self.game.is_ongoing())
        self.assertTrue(self.game.is_finished())


class MasterModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create()
        game = gmodels.Game.objects.create()
        gmodels.Master.objects.create(user=user, game=game)

    def setUp(self):
        self.master = gmodels.Master.objects.last()

    def test_user_type(self):
        user = self.master._meta.get_field("user")
        self.assertTrue(user, models.OneToOneField)

    def test_game_type(self):
        game = self.master._meta.get_field("game")
        self.assertTrue(game, models.OneToOneField)

    def test_str(self):
        self.assertEqual(str(self.master), self.master.user.username)


class PlayerModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username=utrandom.ascii_letters_string(18))
        character = cmodels.Character.objects.create(
            name=utrandom.ascii_letters_string(18)
        )
        game = gmodels.Game.objects.create()
        gmodels.Player.objects.create(user=user, character=character, game=game)

    def setUp(self):
        self.player = gmodels.Player.objects.last()

    def test_user_type(self):
        user = self.player._meta.get_field("user")
        self.assertTrue(user, models.ForeignKey)

    def test_character_type(self):
        character = self.player._meta.get_field("character")
        self.assertTrue(character, models.ForeignKey)

    def test_game_type(self):
        game = self.player._meta.get_field("game")
        self.assertTrue(game, models.ForeignKey)

    def test_str(self):
        self.assertEqual(str(self.player), self.player.user.username)


class EventModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = gmodels.Game.objects.create()
        gmodels.Event.objects.create(game=game)

    def setUp(self):
        self.event = gmodels.Event.objects.last()

    def test_game_type(self):
        game = self.event._meta.get_field("game")
        self.assertTrue(game, models.ForeignKey)

    def test_date_type(self):
        date = self.event._meta.get_field("date")
        self.assertTrue(date, models.DateTimeField)

    def test_date_default_value(self):
        self.assertEqual(self.event.date.second, timezone.now().second)

    def test_message_type(self):
        message = self.event._meta.get_field("message")
        self.assertTrue(message, models.CharField)

    def test_message_max_length(self):
        max_length = self.event._meta.get_field("message").max_length
        self.assertEqual(max_length, 100)

    def test_str(self):
        self.assertEqual(str(self.event), self.event.message)


class TaleModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = gmodels.Game.objects.create()
        gmodels.Tale.objects.create(game=game)

    def setUp(self):
        self.tale = gmodels.Tale.objects.last()

    def test_content_type(self):
        content = self.tale._meta.get_field("content")
        self.assertTrue(content, models.CharField)

    def test_content_max_length(self):
        max_length = self.tale._meta.get_field("content").max_length
        self.assertEqual(max_length, 1000)

    def test_str(self):
        self.assertEqual(str(self.tale), self.tale.content)


class PendingActionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = gmodels.Game.objects.create()
        character = cmodels.Character.objects.get_or_create(id=1)[0]
        gmodels.PendingAction.objects.create(game=game, character=character)

    def setUp(self):
        self.pending_action = gmodels.PendingAction.objects.last()

    def test_character_type(self):
        character = self.pending_action._meta.get_field("character")
        self.assertTrue(character, models.OneToOneField)

    def test_action_type_type(self):
        action_type = self.pending_action._meta.get_field("action_type")
        self.assertTrue(action_type, models.CharField)

    def test_action_type_max_length(self):
        max_length = self.pending_action._meta.get_field("action_type").max_length
        self.assertEqual(max_length, 1)

    def test_str(self):
        self.assertEqual(str(self.pending_action), self.pending_action.action_type)


class XpIncreaseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = gmodels.Game.objects.create()
        character = cmodels.Character.objects.create()
        gmodels.XpIncrease.objects.create(
            game=game, character=character, xp=random.randint(1, 20)
        )

    def setUp(self):
        self.xp_increase = gmodels.XpIncrease.objects.last()

    def test_hp_type(self):
        xp = self.xp_increase._meta.get_field("xp")
        self.assertTrue(xp, models.SmallIntegerField)

    def test_str(self):
        self.assertEqual(str(self.xp_increase), str(self.xp_increase.xp))


class DamageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = gmodels.Game.objects.create()
        character = cmodels.Character.objects.create()
        gmodels.Damage.objects.create(
            game=game, character=character, hp=random.randint(1, 20)
        )

    def setUp(self):
        self.damage = gmodels.Damage.objects.last()

    def test_hp_type(self):
        hp = self.damage._meta.get_field("hp")
        self.assertTrue(hp, models.SmallIntegerField)

    def test_str(self):
        self.assertEqual(str(self.damage), str(self.damage.hp))


class HealingModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = gmodels.Game.objects.create()
        character = cmodels.Character.objects.create()
        gmodels.Healing.objects.create(
            game=game, character=character, hp=random.randint(1, 20)
        )

    def setUp(self):
        self.healing = gmodels.Healing.objects.last()

    def test_hp_type(self):
        hp = self.healing._meta.get_field("hp")
        self.assertTrue(hp, models.SmallIntegerField)

    def test_str(self):
        self.assertEqual(str(self.healing), str(self.healing.hp))


class DiceLaunchModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = gmodels.Game.objects.create()
        character = cmodels.Character.objects.create()
        gmodels.DiceLaunch.objects.create(
            game=game, character=character, score=random.randint(1, 20)
        )

    def setUp(self):
        self.dice_launch = gmodels.DiceLaunch.objects.last()

    def test_character_type(self):
        character = self.dice_launch._meta.get_field("character")
        self.assertTrue(character, models.ForeignKey)

    def test_score_type(self):
        score = self.dice_launch._meta.get_field("score")
        self.assertTrue(score, models.SmallIntegerField)

    def test_str(self):
        self.assertEqual(str(self.dice_launch), str(self.dice_launch.score))


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
