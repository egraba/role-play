from django.contrib.auth.models import User
from django.db import models
from django.test import TestCase
from faker import Faker

from utils.dices import Dice
from character.models import Character


class CharacterModelTest(TestCase):
    fixtures = ["advancement"]

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create()
        Character.objects.create(user=user)

    def setUp(self):
        self.character = Character.objects.last()

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

    def test_class_name_type(self):
        class_name = self.character._meta.get_field("class_name")
        self.assertTrue(class_name, models.CharField)

    def test_class_name_max_length(self):
        max_length = self.character._meta.get_field("class_name").max_length
        self.assertEqual(max_length, 1)

    def test_level_type(self):
        level = self.character._meta.get_field("level")
        self.assertTrue(level, models.SmallIntegerField)

    def test_level_default_value(self):
        self.assertEqual(self.character.level, 1)

    def test_xp_type(self):
        xp = self.character._meta.get_field("xp")
        self.assertTrue(xp, models.IntegerField)

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

    def test_proficiency_bonus_type(self):
        pb = self.character._meta.get_field("proficiency_bonus")
        self.assertTrue(pb, models.SmallIntegerField)

    def test_proficiency_bonus_default_value(self):
        self.assertEqual(self.character.proficiency_bonus, 2)

    def test_strength_type(self):
        strength = self.character._meta.get_field("strength")
        self.assertTrue(strength, models.SmallIntegerField)

    def test_strength_default_value(self):
        self.assertEqual(self.character.strength, 0)

    def test_dexterity_type(self):
        dexterity = self.character._meta.get_field("dexterity")
        self.assertTrue(dexterity, models.SmallIntegerField)

    def test_dexterity_default_value(self):
        self.assertEqual(self.character.dexterity, 0)

    def test_constitution_type(self):
        constitution = self.character._meta.get_field("constitution")
        self.assertTrue(constitution, models.SmallIntegerField)

    def test_constitution_default_value(self):
        self.assertEqual(self.character.constitution, 0)

    def test_intelligence_type(self):
        intelligence = self.character._meta.get_field("intelligence")
        self.assertTrue(intelligence, models.SmallIntegerField)

    def test_intelligence_default_value(self):
        self.assertEqual(self.character.intelligence, 0)

    def test_wisdom_type(self):
        wisdom = self.character._meta.get_field("wisdom")
        self.assertTrue(wisdom, models.SmallIntegerField)

    def test_wisdom_default_value(self):
        self.assertEqual(self.character.wisdom, 0)

    def test_charisma_type(self):
        charisma = self.character._meta.get_field("charisma")
        self.assertTrue(charisma, models.SmallIntegerField)

    def test_charisma_default_value(self):
        self.assertEqual(self.character.charisma, 0)

    def test_gender_type(self):
        gender = self.character._meta.get_field("gender")
        self.assertTrue(gender, models.CharField)

    def test_gender_default_value(self):
        self.assertEqual(self.character.gender, Character.Gender.MALE)

    def test_ac_type(self):
        ac = self.character._meta.get_field("ac")
        self.assertTrue(ac, models.SmallIntegerField)

    def test_ac_default_value(self):
        self.assertEqual(self.character.ac, 0)

    def test_str(self):
        self.assertEqual(str(self.character), self.character.name)

    def test_xp_increase_no_level_increase(self):
        fake = Faker()
        new_xp = fake.random_int(max=200)
        old_xp = self.character.xp
        self.character.increase_xp(new_xp)
        self.assertEqual(self.character.xp, old_xp + new_xp)

    def test_xp_increase_one_level_increase(self):
        fake = Faker()
        new_xp = fake.random_int(min=300, max=500)
        old_xp = self.character.xp
        old_level = self.character.level
        old_bonus = self.character.proficiency_bonus
        old_throws = Dice(self.character.hit_dice).throws
        old_max_hp = self.character.max_hp
        self.character.increase_xp(new_xp)
        self.assertEqual(self.character.xp, old_xp + new_xp)
        self.assertEqual(self.character.level, old_level + 1)
        self.assertEqual(self.character.proficiency_bonus, old_bonus + 2)
        dice = self.character.hit_dice
        self.assertEqual(dice.throws, old_throws + 1)
        self.assertEqual(self.character.max_hp, old_max_hp + self.character.hp_increase)

    def test_xp_increase_several_level_increase(self):
        new_xp = 50_000
        old_xp = self.character.xp
        old_throws = Dice(self.character.hit_dice).throws
        old_max_hp = self.character.max_hp
        self.character.increase_xp(new_xp)
        self.assertEqual(self.character.xp, old_xp + new_xp)
        self.assertEqual(self.character.level, 9)
        self.assertEqual(self.character.proficiency_bonus, 24)
        dice = self.character.hit_dice
        self.assertEqual(dice.throws, old_throws + 8)
        self.assertEqual(
            self.character.max_hp, old_max_hp + self.character.hp_increase * 8
        )
