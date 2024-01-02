import pytest
from faker import Faker

from utils.dices import Dice, DiceError, types


def test_constructor_valid_dice():
    fake = Faker()
    number_of_throws = fake.random_int(min=1, max=10)
    dice_type = fake.random_element(elements=types)
    dice_str = f"{number_of_throws}d{dice_type}"
    dice = Dice(dice_str=dice_str)
    assert dice.throws == number_of_throws
    assert dice.type == dice_type
    assert str(dice) == dice_str


def test_constructor_invalid_dice_str():
    fake = Faker()
    dice_str = fake.pystr(max_chars=5)
    with pytest.raises(TypeError):
        Dice(dice_str)


def test_constructor_invalid_dice_type():
    fake = Faker()
    number_of_throws = fake.random_int(min=1, max=10)
    dice_type = fake.random_element(elements=(2, 3, 5, 100))
    dice_str = f"{number_of_throws}d{dice_type}"
    with pytest.raises(DiceError):
        Dice(dice_str)
