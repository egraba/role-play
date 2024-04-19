import pytest
from faker import Faker

from character.utils.equipment.parsers import parse_ac_settings


def test_parse_ac_settings_ac_only():
    settings_str = "11"
    assert parse_ac_settings(settings_str) == (11, 0, 0)


def test_parse_ac_settings_ac_only_wrong_format():
    fake = Faker()
    settings_str = fake.random_letter()
    with pytest.raises(ValueError):
        parse_ac_settings(settings_str)


def test_parse_ac_settings_plus_prefix():
    settings_str = "+2"
    assert parse_ac_settings(settings_str) == (0, 0, 2)


def test_parse_ac_settings_plus_prefix_wrong_format():
    fake = Faker()
    settings_str = f"+{fake.random_letters()}"
    with pytest.raises(ValueError):
        parse_ac_settings(settings_str)
