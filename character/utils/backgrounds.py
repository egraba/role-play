from ..constants.equipment import GearType, ToolType
from ..models.character import Character
from ..models.equipment import Gear, Tool
from ..models.races import Language


def get_non_spoken_languages(character: Character) -> set[tuple[str, str]]:
    """
    Return the set of language names a character does not speak.
    """
    languages = set(Language.objects.all())
    character_languages = set(character.languages.all())
    return {
        (language.name, language.get_name_display())
        for language in languages
        if language not in character_languages
    }


def get_holy_symbols() -> set[tuple[str, str]]:
    """
    Return the set of all holy symbols names.
    """
    return {
        (gear.name, gear.get_name_display())
        for gear in Gear.objects.filter(gear_type=GearType.HOLY_SYMBOL)
    }


def get_gaming_set_tools() -> set[tuple[str, str]]:
    """
    Return the set of gaming set tools names.
    """
    return {
        (tool.name, tool.get_name_display())
        for tool in Tool.objects.filter(tool_type=ToolType.GAMING_SET)
    }


def get_artisans_tools() -> set[tuple[str, str]]:
    """
    Return the set of artisan's tools names.
    """
    return {
        (tool.name, tool.get_name_display())
        for tool in Tool.objects.filter(tool_type=ToolType.ARTISANS_TOOLS)
    }
