import pytest
from faker import Faker

from utils.dice import DiceString, DiceStringFormatError, dice_types


@pytest.fixture
def dice_str():
    fake = Faker()
    nb_throws = fake.random_int(min=1, max=10)
    dice_type = fake.random_element(elements=dice_types)
    return DiceString(f"{nb_throws}d{dice_type}")


@pytest.fixture
def dice_str_no_throw():
    fake = Faker()
    dice_type = fake.random_element(elements=dice_types)
    return DiceString(f"d{dice_type}")


def test_constructor_valid_dice_str(dice_str, dice_str_no_throw):
    assert dice_str == f"{dice_str.nb_throws}d{dice_str.dice_type}"
    assert dice_str_no_throw == f"d{dice_str_no_throw.dice_type}"


def test_constructor_invalid_dice_str():
    fake = Faker()
    with pytest.raises(DiceStringFormatError):
        DiceString(fake.pystr(max_chars=5))


def test_constructor_invalid_dice_type():
    fake = Faker()
    nb_throws = fake.random_int(min=1, max=10)
    dice_type = fake.random_element(elements=(2, 3, 5, 100))
    with pytest.raises(DiceStringFormatError):
        DiceString(f"{nb_throws}d{dice_type}")


def test_add_throws_valid_nb_throws(dice_str):
    fake = Faker()
    nb_throws = fake.random_int(min=1, max=10)
    old_throws = dice_str.nb_throws
    assert (
        dice_str.add_throws(nb_throws)
        == f"{old_throws + nb_throws}d{dice_str.dice_type}"
    )


def test_add_throws_no_throw_dice_str(dice_str_no_throw):
    fake = Faker()
    nb_throws = fake.random_int(min=1, max=10)
    old_throws = dice_str_no_throw.nb_throws
    assert (
        dice_str_no_throw.add_throws(nb_throws)
        == f"{old_throws + nb_throws}d{dice_str_no_throw.dice_type}"
    )


def test_add_throws_invalid_nb_throws(dice_str):
    fake = Faker()
    nb_throws = fake.random_int(min=-10, max=0)
    with pytest.raises(DiceStringFormatError):
        dice_str.add_throws(nb_throws)


def test_roll_one_throw(dice_str_no_throw):
    roll = dice_str_no_throw.roll()
    assert roll <= dice_str_no_throw.dice_type


def test_roll_several_throws(dice_str):
    roll = dice_str.roll()
    assert roll <= dice_str.dice_type * dice_str.nb_throws


def test_roll_with_modifier(dice_str):
    fake = Faker()
    min_modifier = -5
    max_modifier = 10
    modifier = fake.random_int(min=min_modifier, max=max_modifier)
    roll = dice_str.roll(modifier)
    assert (
        1 * dice_str.nb_throws + min_modifier
        <= roll
        <= dice_str.dice_type * dice_str.nb_throws + max_modifier
    )
