from unittest import TestCase

from faker import Faker

from utils.dices import Dice, DiceError, types


class DiceTest(TestCase):
    def test_constructor_valid_dice(self):
        fake = Faker()
        number_of_throws = fake.random_int(min=1, max=10)
        dice_type = fake.random_element(elements=types)
        dice_str = f"{number_of_throws}d{dice_type}"
        dice = Dice(dice_str=dice_str)
        self.assertEqual(dice.throws, number_of_throws)
        self.assertEqual(dice.type, dice_type)
        self.assertEquals(str(dice), dice_str)

    def test_constructor_invalid_dice_str(self):
        fake = Faker()
        dice_str = fake.pystr(max_chars=5)
        with self.assertRaises(TypeError):
            Dice(dice_str)

    def test_constructor_invalid_dice_type(self):
        fake = Faker()
        number_of_throws = fake.random_int(min=1, max=10)
        dice_type = fake.random_element(elements=(2, 3, 5, 100))
        dice_str = f"{number_of_throws}d{dice_type}"
        with self.assertRaises(DiceError):
            Dice(dice_str)
