import pytest
from faker import Faker

from utils.dice import Dice, DiceStringFormatError, dice_types


@pytest.fixture
def dice_str():
    fake = Faker()
    dice_throws = fake.random_int(min=1, max=10)
    dice_type = fake.random_element(elements=dice_types)
    return Dice(f"{dice_throws}d{dice_type}")


@pytest.fixture
def dice_str_no_throw():
    fake = Faker()
    dice_type = fake.random_element(elements=dice_types)
    return Dice(f"d{dice_type}")


def test_constructor_valid_dice(dice_str, dice_str_no_throw):
    assert dice_str == f"{dice_str.throws}d{dice_str.type}"
    assert dice_str_no_throw == f"d{dice_str_no_throw.type}"


def test_constructor_invalid_dice_str():
    fake = Faker()
    with pytest.raises(DiceStringFormatError):
        Dice(fake.pystr(max_chars=5))


def test_constructor_invalid_dice_type():
    fake = Faker()
    dice_throws = fake.random_int(min=1, max=10)
    dice_type = fake.random_element(elements=(2, 3, 5, 100))
    with pytest.raises(DiceStringFormatError):
        Dice(f"{dice_throws}d{dice_type}")


def test_add_throws_valid_thows(dice_str):
    fake = Faker()
    number_of_throws = fake.random_int(min=1, max=10)
    old_throws = dice_str.throws
    assert (
        dice_str.add_throws(number_of_throws)
        == f"{old_throws + number_of_throws}d{dice_str.type}"
    )


def test_add_throws_no_throw(dice_str_no_throw):
    fake = Faker()
    number_of_throws = fake.random_int(min=1, max=10)
    old_throws = dice_str_no_throw.throws
    assert (
        dice_str_no_throw.add_throws(number_of_throws)
        == f"{old_throws + number_of_throws}d{dice_str_no_throw.type}"
    )


def test_add_throws_invalid_thows(dice_str):
    fake = Faker()
    number_of_throws = fake.random_int(min=-10, max=0)
    with pytest.raises(DiceStringFormatError):
        dice_str.add_throws(number_of_throws)


def test_roll_one_throw(dice_str_no_throw):
    roll = dice_str_no_throw.roll()
    assert roll <= dice_str_no_throw.type


def test_roll_several_throws(dice_str):
    roll = dice_str.roll()
    assert roll <= dice_str.type * dice_str.throws


def test_roll_with_modifier(dice_str):
    fake = Faker()
    min_modifier = -5
    max_modifier = 10
    modifier = fake.random_int(min=min_modifier, max=max_modifier)
    roll = dice_str.roll(modifier)
    assert (
        1 * dice_str.throws + min_modifier
        <= roll
        <= dice_str.type * dice_str.throws + max_modifier
    )
