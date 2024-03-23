import pytest
from faker import Faker

from character.constants.equipment import GearType, ToolType
from character.constants.races import LanguageName
from character.models.equipment import Gear, Tool
from character.models.races import Language
from character.utils.backgrounds import (
    get_artisans_tools,
    get_gaming_set_tools,
    get_holy_symbols,
    get_non_spoken_languages,
)

from ..factories import CharacterFactory


@pytest.mark.django_db
def test_get_non_spoken_languages():
    character = CharacterFactory()
    fake = Faker()
    character.languages.add(Language.objects.get(name=fake.enum(enum_cls=LanguageName)))
    character.languages.add(Language.objects.get(name=fake.enum(enum_cls=LanguageName)))
    character_languages = {
        (language.name, language.get_name_display())
        for language in character.languages.all()
    }
    language_choices = get_non_spoken_languages(character)
    assert character_languages & language_choices == set()
    languages = {
        (language.name, language.get_name_display())
        for language in Language.objects.all()
    }
    assert language_choices < languages


@pytest.mark.django_db
def test_get_holy_symbols():
    holy_symbols = {
        (gear.name, gear.get_name_display())
        for gear in Gear.objects.filter(gear_type=GearType.HOLY_SYMBOL)
    }
    assert get_holy_symbols() == holy_symbols


@pytest.mark.django_db
def test_get_gaming_set_tools():
    gaming_set_tools = {
        (tool.name, tool.get_name_display())
        for tool in Tool.objects.filter(tool_type=ToolType.GAMING_SET)
    }
    assert get_gaming_set_tools() == gaming_set_tools


@pytest.mark.django_db
def test_get_artisans_tools():
    artisans_tools = {
        (tool.name, tool.get_name_display())
        for tool in Tool.objects.filter(tool_type=ToolType.ARTISANS_TOOLS)
    }
    assert get_artisans_tools() == artisans_tools
