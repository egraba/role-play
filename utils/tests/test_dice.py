import pytest
from faker import Faker

from utils.dice import Dice, DiceFormatError, types


def test_constructor_valid_dice():
    fake = Faker()
    dice_throws = fake.random_int(min=1, max=10)
    dice_type = fake.random_element(elements=types)
    dice_str = Dice(f"{dice_throws}d{dice_type}")
    assert dice_str == f"{dice_throws}d{dice_type}"


def test_constructor_invalid_dice_str():
    fake = Faker()
    with pytest.raises(DiceFormatError):
        Dice(fake.pystr(max_chars=5))


def test_constructor_invalid_dice_type():
    fake = Faker()
    dice_throws = fake.random_int(min=1, max=10)
    dice_type = fake.random_element(elements=(2, 3, 5, 100))
    with pytest.raises(DiceFormatError):
        Dice(f"{dice_throws}d{dice_type}")


def test_add_throws_valid_dice():
    fake = Faker()
    dice_throws = fake.random_int(min=1, max=10)
    dice_type = fake.random_element(elements=types)
    dice_str = Dice(f"{dice_throws}d{dice_type}")
    number_of_throws = fake.random_int(min=1, max=10)
    assert (
        dice_str.add_throws(number_of_throws)
        == f"{dice_throws + number_of_throws}d{dice_type}"
    )
