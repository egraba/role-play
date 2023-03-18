import random

from django.db import models
from django.test import TestCase
from django.utils import timezone

from game.models import (
    Character,
    Choice,
    Damage,
    DiceLaunch,
    Event,
    Game,
    Healing,
    PendingAction,
    Tale,
    XpIncrease,
)
from game.tests import utils


class GameModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Game.objects.create(name=utils.generate_random_string(50))

    def test_name_type(self):
        game = Game.objects.last()
        name = game._meta.get_field("name")
        self.assertTrue(name, models.CharField)

    def test_name_max_length(self):
        game = Game.objects.last()
        max_length = game._meta.get_field("name").max_length
        self.assertEqual(max_length, 50)

    def test_start_date_type(self):
        game = Game.objects.last()
        start_date = game._meta.get_field("start_date")
        self.assertTrue(start_date, models.DateTimeField)

    def test_end_date_type(self):
        game = Game.objects.last()
        end_date = game._meta.get_field("end_date")
        self.assertTrue(end_date, models.DateTimeField)

    def test_end_date_default_value(self):
        game = Game.objects.last()
        self.assertEqual(game.end_date, None)

    def test_status_type(self):
        game = Game.objects.last()
        status = game._meta.get_field("status")
        self.assertTrue(status, models.CharField)

    def test_str_is_name(self):
        game = Game.objects.last()
        self.assertEqual(str(game), game.name)


class CharacterModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Character.objects.create()

    def test_game_type(self):
        character = Character.objects.last()
        game = character._meta.get_field("game")
        self.assertTrue(game, models.ForeignKey)

    def test_name_type(self):
        character = Character.objects.last()
        name = character._meta.get_field("name")
        self.assertTrue(name, models.CharField)

    def test_name_max_length(self):
        character = Character.objects.last()
        max_length = character._meta.get_field("name").max_length
        self.assertEqual(max_length, 100)

    def test_name_uniqueness(self):
        character = Character.objects.last()
        is_unique = character._meta.get_field("name").unique
        self.assertTrue(is_unique)

    def test_race_type(self):
        character = Character.objects.last()
        race = character._meta.get_field("race")
        self.assertTrue(race, models.CharField)

    def test_race_max_length(self):
        character = Character.objects.last()
        max_length = character._meta.get_field("race").max_length
        self.assertEqual(max_length, 1)

    def test_xp_type(self):
        character = Character.objects.last()
        xp = character._meta.get_field("xp")
        self.assertTrue(xp, models.SmallIntegerField)

    def test_xp_default_value(self):
        character = Character.objects.last()
        self.assertEqual(character.xp, 0)

    def test_hp_type(self):
        character = Character.objects.last()
        hp = character._meta.get_field("hp")
        self.assertTrue(hp, models.SmallIntegerField)

    def test_hp_default_value(self):
        character = Character.objects.last()
        self.assertEqual(character.hp, 100)

    def test_max_hp_type(self):
        character = Character.objects.last()
        max_hp = character._meta.get_field("max_hp")
        self.assertTrue(max_hp, models.SmallIntegerField)

    def test_max_hp_default_value(self):
        character = Character.objects.last()
        self.assertEqual(character.max_hp, 100)

    def test_str(self):
        character = Character.objects.last()
        self.assertEqual(str(character), character.name)


class EventModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        Event.objects.create(game=game)

    def test_game_type(self):
        event = Event.objects.last()
        game = event._meta.get_field("game")
        self.assertTrue(game, models.ForeignKey)

    def test_date_type(self):
        event = Event.objects.last()
        date = event._meta.get_field("date")
        self.assertTrue(date, models.DateTimeField)

    def test_date_default_value(self):
        event = Event.objects.last()
        self.assertEqual(event.date.second, timezone.now().second)

    def test_message_type(self):
        event = Event.objects.last()
        message = event._meta.get_field("message")
        self.assertTrue(message, models.CharField)

    def test_message_max_length(self):
        event = Event.objects.last()
        max_length = event._meta.get_field("message").max_length
        self.assertEqual(max_length, 100)

    def test_str(self):
        event = Event.objects.last()
        self.assertEqual(str(event), event.message)


class TaleModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        Tale.objects.create(game=game)

    def test_description_type(self):
        tale = Tale.objects.last()
        description = tale._meta.get_field("description")
        self.assertTrue(description, models.CharField)

    def test_message_max_length(self):
        tale = Tale.objects.last()
        max_length = tale._meta.get_field("description").max_length
        self.assertEqual(max_length, 1000)

    def test_str(self):
        tale = Tale.objects.last()
        self.assertEqual(str(tale), tale.description)


class XpIncreaseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        character = Character.objects.create()
        XpIncrease.objects.create(
            game=game, character=character, xp=random.randint(1, 20)
        )

    def test_hp_type(self):
        xp_increase = XpIncrease.objects.last()
        xp = xp_increase._meta.get_field("xp")
        self.assertTrue(xp, models.SmallIntegerField)

    def test_str(self):
        xp_increase = XpIncrease.objects.last()
        self.assertEqual(str(xp_increase), str(xp_increase.xp))


class DamageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        Damage.objects.create(game=game, hp=random.randint(1, 20))

    def test_hp_type(self):
        damage = Damage.objects.last()
        hp = damage._meta.get_field("hp")
        self.assertTrue(hp, models.SmallIntegerField)

    def test_str(self):
        damage = Damage.objects.last()
        self.assertEqual(str(damage), str(damage.hp))


class HealingModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        Healing.objects.create(game=game, hp=random.randint(1, 20))

    def test_hp_type(self):
        healing = Healing.objects.last()
        hp = healing._meta.get_field("hp")
        self.assertTrue(hp, models.SmallIntegerField)

    def test_str(self):
        healing = Healing.objects.last()
        self.assertEqual(str(healing), str(healing.hp))


class PendingActionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        character = Character.objects.get_or_create(id=1)[0]
        PendingAction.objects.create(game=game, character=character)

    def test_character_type(self):
        pending_action = PendingAction.objects.last()
        character = pending_action._meta.get_field("character")
        self.assertTrue(character, models.ForeignKey)

    def test_action_type_type(self):
        pending_action = PendingAction.objects.last()
        action_type = pending_action._meta.get_field("action_type")
        self.assertTrue(action_type, models.CharField)

    def test_action_type_max_length(self):
        pending_action = PendingAction.objects.last()
        max_length = pending_action._meta.get_field("action_type").max_length
        self.assertEqual(max_length, 1)

    def test_str(self):
        pending_action = PendingAction.objects.last()
        self.assertEqual(str(pending_action), pending_action.action_type)


class DiceLaunchModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        character = Character.objects.create()
        DiceLaunch.objects.create(
            game=game, character=character, score=random.randint(1, 20)
        )

    def test_character_type(self):
        dice_launch = DiceLaunch.objects.last()
        character = dice_launch._meta.get_field("character")
        self.assertTrue(character, models.ForeignKey)

    def test_score_type(self):
        dice_launch = DiceLaunch.objects.last()
        score = dice_launch._meta.get_field("score")
        self.assertTrue(score, models.SmallIntegerField)

    def test_str(self):
        dice_launch = DiceLaunch.objects.last()
        self.assertEqual(str(dice_launch), str(dice_launch.score))


class ChoiceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create()
        character = Character.objects.create()
        Choice.objects.create(
            game=game, character=character, selection=utils.generate_random_string(200)
        )

    def test_character_type(self):
        choice = Choice.objects.last()
        character = choice._meta.get_field("character")
        self.assertTrue(character, models.ForeignKey)

    def test_selection_type(self):
        choice = Choice.objects.last()
        selection = choice._meta.get_field("selection")
        self.assertTrue(selection, models.SmallIntegerField)

    def test_selection_max_length(self):
        choice = Choice.objects.last()
        max_length = choice._meta.get_field("selection").max_length
        self.assertEqual(max_length, 300)

    def test_str(self):
        choice = Choice.objects.last()
        self.assertEqual(str(choice), choice.selection)
