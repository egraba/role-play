from django.contrib.auth.models import User
from django.db import models
from django.test import TestCase

import character.models as cmodels


class CharacterModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create()
        cmodels.Character.objects.create(user=user)

    def setUp(self):
        self.character = cmodels.Character.objects.last()

    def test_name_type(self):
        name = self.character._meta.get_field("name")
        self.assertTrue(name, models.CharField)

    def test_name_max_length(self):
        max_length = self.character._meta.get_field("name").max_length
        self.assertEqual(max_length, 100)

    def test_name_uniqueness(self):
        is_unique = self.character._meta.get_field("name").unique
        self.assertTrue(is_unique)

    def test_user_type(self):
        user = self.character._meta.get_field("user")
        self.assertTrue(user, models.OneToOneField)

    def test_race_type(self):
        race = self.character._meta.get_field("race")
        self.assertTrue(race, models.CharField)

    def test_race_max_length(self):
        max_length = self.character._meta.get_field("race").max_length
        self.assertEqual(max_length, 1)

    def test_level_type(self):
        level = self.character._meta.get_field("level")
        self.assertTrue(level, models.SmallIntegerField)

    def test_level_default_value(self):
        self.assertEqual(self.character.level, 1)

    def test_xp_type(self):
        xp = self.character._meta.get_field("xp")
        self.assertTrue(xp, models.SmallIntegerField)

    def test_xp_default_value(self):
        self.assertEqual(self.character.xp, 0)

    def test_hp_type(self):
        hp = self.character._meta.get_field("hp")
        self.assertTrue(hp, models.SmallIntegerField)

    def test_hp_default_value(self):
        self.assertEqual(self.character.hp, 100)

    def test_max_hp_type(self):
        max_hp = self.character._meta.get_field("max_hp")
        self.assertTrue(max_hp, models.SmallIntegerField)

    def test_max_hp_default_value(self):
        self.assertEqual(self.character.max_hp, 100)

    def test_str(self):
        self.assertEqual(str(self.character), self.character.name)
