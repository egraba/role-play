import pytest
from faker import Faker

from equipment.constants.equipment import DamageType
from equipment.utils.equipment_parsers import (
    parse_ac_settings,
    parse_damage,
    parse_strength,
)


def test_parse_ac_settings_ac_only():
    settings_str = "11"
    assert parse_ac_settings(settings_str) == (11, False, 0, 0)


def test_parse_ac_settings_ac_only_wrong_format():
    fake = Faker()
    settings_str = fake.random_letter()
    with pytest.raises(ValueError):
        parse_ac_settings(settings_str)


def test_parse_ac_settings_plus_prefix():
    settings_str = "+2"
    assert parse_ac_settings(settings_str) == (0, False, 0, 2)


def test_parse_ac_settings_plus_prefix_wrong_format():
    fake = Faker()
    settings_str = f"+{fake.random_letters()}"
    with pytest.raises(ValueError):
        parse_ac_settings(settings_str)


def test_parse_ac_settings_dex_modifier():
    settings_str = "12 + Dex modifier"
    assert parse_ac_settings(settings_str) == (12, True, 0, 0)


def test_parse_ac_settings_dex_modifier_max():
    settings_str = "12 + Dex modifier (max 2)"
    assert parse_ac_settings(settings_str) == (12, True, 2, 0)


def test_parse_strength_empty():
    settings_str = None
    assert parse_strength(settings_str) == 0
    settings_str = ""
    assert parse_strength(settings_str) == 0


def test_parse_strength_good_format():
    settings_str = "Str 15"
    assert parse_strength(settings_str) == 15


def test_parse_strength_wrong_format():
    settings_str = "Dex 20"
    assert parse_strength(settings_str) == 0


def test_parse_damage_valid_format():
    settings_str = "1d8 slashing"
    assert parse_damage(settings_str) == ("1d8", DamageType.SLASHING)


def test_parse_damage_invalid_dice_str():
    settings_str = "1d40 slashing"
    with pytest.raises(ValueError):
        parse_damage(settings_str)


def test_parse_damage_invalid_action():
    settings_str = "1d6 something"
    with pytest.raises(ValueError):
        parse_damage(settings_str)
