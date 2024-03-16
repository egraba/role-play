import pytest
from faker import Faker

from character.constants.equipment import GearType, ToolType
from character.constants.races import LanguageName
from character.models.equipment import Gear, Tool
from character.models.races import Language
from character.utils.backgrounds import (
    get_holy_symbols,
    get_non_spoken_languages,
    get_gaming_set_tools,
)

from ..factories import CharacterFactory


@pytest.mark.django_db
def test_get_non_spoken_languages():
    character = CharacterFactory()
    fake = Faker()
    character.languages.add(Language.objects.get(name=fake.enum(enum_cls=LanguageName)))
    character.languages.add(Language.objects.get(name=fake.enum(enum_cls=LanguageName)))
    character_languages = set(character.languages.all())
    language_choices = get_non_spoken_languages(character)
    assert character_languages & language_choices == set()
    languages = set(Language.objects.all())
    assert language_choices < languages


@pytest.mark.django_db
def test_get_holy_symbols():
    holy_symbols = set(Gear.objects.filter(gear_type=GearType.HOLY_SYMBOL))
    assert get_holy_symbols() == holy_symbols


@pytest.mark.django_db
def test_get_gaming_set_tools():
    gaming_set_tools = set(Tool.objects.filter(tool_type=ToolType.GAMING_SET))
    assert get_gaming_set_tools() == gaming_set_tools