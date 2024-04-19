from character.utils.equipment.parsers import parse_ac_settings


def test_parse_ac_settings_ac_only():
    settings_str = "11"
    assert parse_ac_settings(settings_str) == (11, 0, 0)
