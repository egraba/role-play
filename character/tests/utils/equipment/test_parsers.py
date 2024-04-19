import pytest
from faker import Faker

from character.utils.equipment.parsers import parse_ac_settings, parse_stealth


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


def test_parse_stealth_empty():
    settings_str = None
    assert parse_stealth(settings_str) == 0
    settings_str = ""
    assert parse_stealth(settings_str) == 0


def test_parse_stealth_good_format():
    settings_str = "Str 15"
    assert parse_stealth(settings_str) == 15


def test_parse_stealth_wrong_format():
    settings_str = "Dex 20"
    assert parse_stealth(settings_str) == 0
