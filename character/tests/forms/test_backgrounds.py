import pytest

from equipment.constants.equipment import GearType, ToolType
from character.forms.backgrounds import (
    _get_gaming_set_tools,
    _get_holy_symbols,
)
from equipment.models.equipment import GearSettings, ToolSettings

pytestmark = pytest.mark.django_db


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
