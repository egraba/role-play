import pytest

from character.constants.equipment import GearType, ToolType
from character.constants.races import RACIAL_TRAITS
from character.forms.backgrounds import (
    _get_artisans_tools,
    _get_gaming_set_tools,
    _get_holy_symbols,
    _get_non_spoken_languages,
)
from character.models.equipment import GearSettings, ToolSettings
from character.models.races import Language

from ..factories import CharacterFactory

pytestmark = pytest.mark.django_db


def test_get_non_spoken_languages():
    character = CharacterFactory()
    race_languages = {
        (language.value, language.label)
        for language in RACIAL_TRAITS[character.race]["languages"]
    }
    language_choices = _get_non_spoken_languages(character.race)
    assert race_languages & language_choices == set()
    all_languages = {
        (language.name, language.get_name_display())
        for language in Language.objects.all()
    }
    assert language_choices < all_languages


def test_get_holy_symbols():
    holy_symbols = {
        (gear.name, gear.get_name_display())
        for gear in GearSettings.objects.filter(gear_type=GearType.HOLY_SYMBOL)
    }
    assert _get_holy_symbols() == holy_symbols


def test_get_gaming_set_tools():
    gaming_set_tools = {
        (tool.name, tool.get_name_display())
        for tool in ToolSettings.objects.filter(tool_type=ToolType.GAMING_SET)
    }
    assert _get_gaming_set_tools() == gaming_set_tools


def test_get_artisans_tools():
    artisans_tools = {
        (tool.name, tool.get_name_display())
        for tool in ToolSettings.objects.filter(tool_type=ToolType.ARTISANS_TOOLS)
    }
    assert _get_artisans_tools() == artisans_tools
