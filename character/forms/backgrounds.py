from django import forms

from ..constants.backgrounds import Background
from ..constants.equipment import GearType, ToolType
from ..constants.races import LanguageName
from ..models.equipment import GearSettings, ToolSettings
from ..models.species import Species


def _get_non_spoken_languages(species: Species | None) -> set[tuple[str, str]]:
    """
    Return the set of language names without the languages spoken by the species.
    """
    all_languages = set(LanguageName.choices)
    if not species:
        return all_languages
    species_languages = {
        (language.name, language.get_name_display())
        for language in species.languages.all()
    }
    return {
        (language[0], language[1])
        for language in all_languages
        if language not in species_languages
    }


def _get_holy_symbols() -> set[tuple[str, str]]:
    """
    Return the set of all holy symbols names.
    """
    return {
        (gear.name, gear.get_name_display())
        for gear in GearSettings.objects.filter(gear_type=GearType.HOLY_SYMBOL)
    }


def _get_gaming_set_tools() -> set[tuple[str, str]]:
    """
    Return the set of gaming set tools names.
    """
    return {
        (tool.name, tool.get_name_display())
        for tool in ToolSettings.objects.filter(tool_type=ToolType.GAMING_SET)
    }


def _get_artisans_tools() -> set[tuple[str, str]]:
    """
    Return the set of artisan's tools names.
    """
    return {
        (tool.name, tool.get_name_display())
        for tool in ToolSettings.objects.filter(tool_type=ToolType.ARTISANS_TOOLS)
    }


class BackgroundForm(forms.Form):
    EMPTY_CHOICE = ("", "---------")

    def _get_choices(self, choices):
        """Return choices with empty choice prepended, or None if no choices."""
        return [self.EMPTY_CHOICE, *choices] if choices else None

    def _add_field_if_choices(self, field_name, choices):
        """Add field only if there are choices available."""
        if choices:
            self.fields[field_name] = forms.ChoiceField(
                choices=choices,
                widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        species_name = self.initial.get("species")
        background = self.initial["background"]

        # Look up Species object by name if provided as string
        species = None
        if species_name:
            species = Species.objects.filter(name=species_name).first()

        language_choices = self._get_choices(_get_non_spoken_languages(species))
        holy_symbols_choices = self._get_choices(_get_holy_symbols())
        artisans_tools_choices = self._get_choices(_get_artisans_tools())
        gaming_set_choices = self._get_choices(_get_gaming_set_tools())

        match background:
            case Background.ACOLYTE:
                self._add_field_if_choices("first_language", language_choices)
                self._add_field_if_choices("second_language", language_choices)
                self._add_field_if_choices("equipment", holy_symbols_choices)
            case Background.CRIMINAL:
                self._add_field_if_choices("tool_proficiency", gaming_set_choices)
            case Background.FOLK_HERO:
                self._add_field_if_choices("tool_proficiency", artisans_tools_choices)
                self._add_field_if_choices("equipment", artisans_tools_choices)
            case Background.NOBLE:
                self._add_field_if_choices("language", language_choices)
                self._add_field_if_choices("tool_proficiency", gaming_set_choices)
            case Background.SAGE:
                self._add_field_if_choices("first_language", language_choices)
                self._add_field_if_choices("second_language", language_choices)
            case Background.SOLDIER:
                self._add_field_if_choices("tool_proficiency", gaming_set_choices)
