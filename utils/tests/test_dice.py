import pytest
from faker import Faker

from utils.dice import DiceString, DiceStringFormatError, dice_types, roll_d20_test


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


class TestRollKeepingIndividual:
    def test_returns_total_and_individual_rolls(self):
        dice_str = DiceString("3d6")
        total, rolls = dice_str.roll_keeping_individual()
        assert len(rolls) == 3
        assert all(1 <= r <= 6 for r in rolls)
        assert total == sum(rolls)

    def test_applies_modifier_to_total(self):
        dice_str = DiceString("2d6")
        total, rolls = dice_str.roll_keeping_individual(modifier=5)
        assert total == sum(rolls) + 5

    def test_single_die(self):
        dice_str = DiceString("d20")
        total, rolls = dice_str.roll_keeping_individual()
        assert len(rolls) == 1
        assert 1 <= rolls[0] <= 20
        assert total == rolls[0]


class TestRollWithAdvantage:
    def test_returns_higher_of_two_rolls(self, monkeypatch):
        rolls_sequence = iter([10, 15])
        monkeypatch.setattr("random.randint", lambda a, b: next(rolls_sequence))
        dice_str = DiceString("d20")
        result, roll1, roll2 = dice_str.roll_with_advantage()
        assert roll1 == 10
        assert roll2 == 15
        assert result == 15

    def test_applies_modifier(self, monkeypatch):
        rolls_sequence = iter([8, 12])
        monkeypatch.setattr("random.randint", lambda a, b: next(rolls_sequence))
        dice_str = DiceString("d20")
        result, _, _ = dice_str.roll_with_advantage(modifier=3)
        assert result == 15  # 12 + 3

    def test_result_within_bounds(self):
        dice_str = DiceString("d20")
        for _ in range(20):
            result, roll1, roll2 = dice_str.roll_with_advantage()
            assert result == max(roll1, roll2)
            assert 1 <= roll1 <= 20
            assert 1 <= roll2 <= 20


class TestRollWithDisadvantage:
    def test_returns_lower_of_two_rolls(self, monkeypatch):
        rolls_sequence = iter([10, 15])
        monkeypatch.setattr("random.randint", lambda a, b: next(rolls_sequence))
        dice_str = DiceString("d20")
        result, roll1, roll2 = dice_str.roll_with_disadvantage()
        assert roll1 == 10
        assert roll2 == 15
        assert result == 10

    def test_applies_modifier(self, monkeypatch):
        rolls_sequence = iter([8, 12])
        monkeypatch.setattr("random.randint", lambda a, b: next(rolls_sequence))
        dice_str = DiceString("d20")
        result, _, _ = dice_str.roll_with_disadvantage(modifier=3)
        assert result == 11  # 8 + 3

    def test_result_within_bounds(self):
        dice_str = DiceString("d20")
        for _ in range(20):
            result, roll1, roll2 = dice_str.roll_with_disadvantage()
            assert result == min(roll1, roll2)
            assert 1 <= roll1 <= 20
            assert 1 <= roll2 <= 20


class TestRollDamage:
    def test_normal_damage_roll(self):
        dice_str = DiceString("2d6")
        damage = dice_str.roll_damage()
        assert 2 <= damage <= 12

    def test_critical_doubles_dice(self, monkeypatch):
        # Mock to return predictable values: first 2d6 = [3,4], second 2d6 = [2,5]
        rolls_sequence = iter([3, 4, 2, 5])
        monkeypatch.setattr("random.randint", lambda a, b: next(rolls_sequence))
        dice_str = DiceString("2d6")
        damage = dice_str.roll_damage(critical=True)
        assert damage == 14  # (3+4) + (2+5)

    def test_critical_damage_bounds(self):
        dice_str = DiceString("1d8")
        for _ in range(20):
            normal = dice_str.roll_damage(critical=False)
            assert 1 <= normal <= 8
        for _ in range(20):
            crit = dice_str.roll_damage(critical=True)
            assert 2 <= crit <= 16  # 2 dice worth


class TestRollD20Test:
    def test_basic_roll(self, monkeypatch):
        monkeypatch.setattr("random.randint", lambda a, b: 15)
        total, is_nat_20, is_nat_1 = roll_d20_test()
        assert total == 15
        assert is_nat_20 is False
        assert is_nat_1 is False

    def test_with_modifier(self, monkeypatch):
        monkeypatch.setattr("random.randint", lambda a, b: 10)
        total, _, _ = roll_d20_test(modifier=5)
        assert total == 15

    def test_detects_natural_20(self, monkeypatch):
        monkeypatch.setattr("random.randint", lambda a, b: 20)
        total, is_nat_20, is_nat_1 = roll_d20_test()
        assert total == 20
        assert is_nat_20 is True
        assert is_nat_1 is False

    def test_detects_natural_1(self, monkeypatch):
        monkeypatch.setattr("random.randint", lambda a, b: 1)
        total, is_nat_20, is_nat_1 = roll_d20_test()
        assert total == 1
        assert is_nat_20 is False
        assert is_nat_1 is True

    def test_advantage_takes_higher(self, monkeypatch):
        rolls_sequence = iter([8, 15])
        monkeypatch.setattr("random.randint", lambda a, b: next(rolls_sequence))
        total, is_nat_20, _ = roll_d20_test(advantage=True)
        assert total == 15

    def test_disadvantage_takes_lower(self, monkeypatch):
        rolls_sequence = iter([8, 15])
        monkeypatch.setattr("random.randint", lambda a, b: next(rolls_sequence))
        total, _, _ = roll_d20_test(disadvantage=True)
        assert total == 8

    def test_advantage_and_disadvantage_cancel_out(self, monkeypatch):
        # When both apply, should only roll once
        call_count = 0

        def mock_randint(a, b):
            nonlocal call_count
            call_count += 1
            return 12

        monkeypatch.setattr("random.randint", mock_randint)
        total, _, _ = roll_d20_test(advantage=True, disadvantage=True)
        assert total == 12
        assert call_count == 1  # Only one roll made

    def test_advantage_detects_natural_20_on_higher(self, monkeypatch):
        rolls_sequence = iter([15, 20])
        monkeypatch.setattr("random.randint", lambda a, b: next(rolls_sequence))
        _, is_nat_20, _ = roll_d20_test(advantage=True)
        assert is_nat_20 is True

    def test_disadvantage_detects_natural_1_on_lower(self, monkeypatch):
        rolls_sequence = iter([1, 15])
        monkeypatch.setattr("random.randint", lambda a, b: next(rolls_sequence))
        _, _, is_nat_1 = roll_d20_test(disadvantage=True)
        assert is_nat_1 is True
