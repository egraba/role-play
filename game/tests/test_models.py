from django.db import models
from django.test import TestCase
from django.utils import timezone

from game.models import Character, Game, Narrative, PendingAction
from game.tests import utils


class GameModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Game.objects.create(name=utils.generate_random_string(50))

    def test_name_type(self):
        game = Game.objects.get(id=1)
        name = game._meta.get_field("name")
        self.assertTrue(name, models.CharField)

    def test_name_max_length(self):
        game = Game.objects.get(id=1)
        max_length = game._meta.get_field("name").max_length
        self.assertEqual(max_length, 50)

    def test_start_date_type(self):
        game = Game.objects.get(id=1)
        start_date = game._meta.get_field("start_date")
        self.assertTrue(start_date, models.DateTimeField)

    def test_end_date_type(self):
        game = Game.objects.get(id=1)
        end_date = game._meta.get_field("end_date")
        self.assertTrue(end_date, models.DateTimeField)

    def test_end_date_default_value(self):
        game = Game.objects.get(id=1)
        self.assertEqual(game.end_date, None)

    def test_str_is_name(self):
        game = Game.objects.get(id=1)
        self.assertEqual(str(game), game.name)


class CharacterModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Character.objects.create()

    def test_game_type(self):
        character = Character.objects.get(id=1)
        game = character._meta.get_field("game")
        self.assertTrue(game, models.ForeignKey)

    def test_name_type(self):
        character = Character.objects.get(id=1)
        name = character._meta.get_field("name")
        self.assertTrue(name, models.CharField)

    def test_name_max_length(self):
        character = Character.objects.get(id=1)
        max_length = character._meta.get_field("name").max_length
        self.assertEqual(max_length, 255)

    def test_race_type(self):
        character = Character.objects.get(id=1)
        race = character._meta.get_field("race")
        self.assertTrue(race, models.CharField)

    def test_race_max_length(self):
        character = Character.objects.get(id=1)
        max_length = character._meta.get_field("race").max_length
        self.assertEqual(max_length, 1)

    def test_xp_type(self):
        character = Character.objects.get(id=1)
        xp = character._meta.get_field("xp")
        self.assertTrue(xp, models.SmallIntegerField)

    def test_xp_default_value(self):
        character = Character.objects.get(id=1)
        self.assertEqual(character.xp, 0)

    def test_hp_type(self):
        character = Character.objects.get(id=1)
        hp = character._meta.get_field("hp")
        self.assertTrue(hp, models.SmallIntegerField)

    def test_hp_default_value(self):
        character = Character.objects.get(id=1)
        self.assertEqual(character.hp, 100)

    def test_max_hp_type(self):
        character = Character.objects.get(id=1)
        max_hp = character._meta.get_field("max_hp")
        self.assertTrue(max_hp, models.SmallIntegerField)

    def test_max_hp_default_value(self):
        character = Character.objects.get(id=1)
        self.assertEqual(character.max_hp, 100)

    def test_str(self):
        character = Character.objects.get(id=1)
        self.assertEqual(str(character), character.name)


class NarrativeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Narrative.objects.create()

    def test_game_type(self):
        narrative = Narrative.objects.get(id=1)
        game = narrative._meta.get_field("game")
        self.assertTrue(game, models.ForeignKey)

    def test_date_type(self):
        narrative = Narrative.objects.get(id=1)
        date = narrative._meta.get_field("date")
        self.assertTrue(date, models.DateTimeField)

    def test_date_default_value(self):
        narrative = Narrative.objects.get(id=1)
        self.assertEqual(narrative.date.second, timezone.now().second)

    def test_message_type(self):
        narrative = Narrative.objects.get(id=1)
        message = narrative._meta.get_field("message")
        self.assertTrue(message, models.CharField)

    def test_message_max_length(self):
        narrative = Narrative.objects.get(id=1)
        max_length = narrative._meta.get_field("message").max_length
        self.assertEqual(max_length, 1000)

    def test_str(self):
        narrative = Narrative.objects.get(id=1)
        self.assertEqual(str(narrative), narrative.message)


class PendingActionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Game.objects.create()
        game = Game.objects.last()
        Character.objects.create()
        character = Character.objects.last()
        Narrative.objects.create()
        narrative = Narrative.objects.last()
        PendingAction.objects.create(
            game=game, character=character, narrative=narrative
        )

    def test_game_type(self):
        pending_action = PendingAction.objects.get(id=1)
        game = pending_action._meta.get_field("game")
        self.assertTrue(game, models.ForeignKey)

    def test_character_type(self):
        pending_action = PendingAction.objects.get(id=1)
        character = pending_action._meta.get_field("character")
        self.assertTrue(character, models.ForeignKey)

    def test_narrative_type(self):
        pending_action = PendingAction.objects.get(id=1)
        narrative = pending_action._meta.get_field("narrative")
        self.assertTrue(narrative, models.ForeignKey)

    def test_action_type_type(self):
        pending_action = PendingAction.objects.get(id=1)
        action_type = pending_action._meta.get_field("action_type")
        self.assertTrue(action_type, models.CharField)

    def test_action_type_max_length(self):
        pending_action = PendingAction.objects.get(id=1)
        max_length = pending_action._meta.get_field("action_type").max_length
        self.assertEqual(max_length, 1)

    def test_str(self):
        pending_action = PendingAction.objects.get(id=1)
        self.assertEqual(str(pending_action), pending_action.action_type)
