from unittest import TestCase

from faker import Faker

import utils.dice as dice


class DiceTest(TestCase):
    def test_add_throws_valid_dice(self):
        fake = Faker()
        number_of_throws = fake.random_int(min=1, max=10)
        old_dice = "1d8"
        new_dice = dice.add_throws(old_dice, number_of_throws)
        self.assertEquals(new_dice, f"{number_of_throws + 1}d8")

    def test_add_throws_invalid_dice(self):
        fake = Faker()
        number_of_throws = fake.random_int(min=1, max=10)
        old_dice = fake.pystr(max_chars=5)
        with self.assertRaises(TypeError):
            dice.add_throws(old_dice, number_of_throws)
