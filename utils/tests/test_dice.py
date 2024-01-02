import pytest
from faker import Faker

from utils.dice import DiceFormatError, add_throws, types


def test_add_throws_valid_dice():
    fake = Faker()
    dice_throws = fake.random_int(min=1, max=10)
    dice_type = fake.random_element(elements=types)
    dice_str = f"{dice_throws}d{dice_type}"
    number_of_throws = fake.random_int(min=1, max=10)
    assert (
        add_throws(dice_str=dice_str, throws=number_of_throws)
        == f"{dice_throws + number_of_throws}d{dice_type}"
    )


def test_constructor_invalid_dice_str():
    fake = Faker()
    dice_str = fake.pystr(max_chars=5)
    number_of_throws = fake.random_int(min=1, max=10)
    with pytest.raises(DiceFormatError):
        add_throws(dice_str=dice_str, throws=number_of_throws)


def test_constructor_invalid_dice_type():
    fake = Faker()
    dice_throws = fake.random_int(min=1, max=10)
    dice_type = fake.random_element(elements=(2, 3, 5, 100))
    dice_str = f"{dice_throws}d{dice_type}"
    number_of_throws = fake.random_int(min=1, max=10)
    with pytest.raises(DiceFormatError):
        add_throws(dice_str=dice_str, throws=number_of_throws)
