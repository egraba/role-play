from django import forms

from ..constants.backgrounds import Background
from ..constants.equipment import GearType, ToolType
from ..constants.races import RACIAL_TRAITS, LanguageName, Race
from ..models.equipment import GearSettings, ToolSettings
from .mixins import DuplicateValuesMixin


def _get_non_spoken_languages(race: Race) -> set[tuple[str, str]]:
    """
    Return the set of language names a character does not speak.
    """
    languages = LanguageName.choices
    character_languages = RACIAL_TRAITS[race]
    return {
        (language[0], language[1])
        for language in languages
        if language not in character_languages
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


class AcolyteForm(DuplicateValuesMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        character = self.initial["character"]
        self.fields["first_language"] = forms.ChoiceField(
            choices=_get_non_spoken_languages(character),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        self.fields["second_language"] = forms.ChoiceField(
            choices=_get_non_spoken_languages(character),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        self.fields["equipment"] = forms.ChoiceField(
            choices=_get_holy_symbols(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class CriminalForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tool_proficiency"] = forms.ChoiceField(
            choices=_get_gaming_set_tools(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class FolkHeroForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tool_proficiency"] = forms.ChoiceField(
            choices=_get_artisans_tools(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        self.fields["equipment"] = forms.ChoiceField(
            choices=_get_artisans_tools(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class NobleForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        character = self.initial["character"]
        self.fields["language"] = forms.ChoiceField(
            choices=_get_non_spoken_languages(character),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        self.fields["tool_proficiency"] = forms.ChoiceField(
            choices=_get_gaming_set_tools(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class SageForm(DuplicateValuesMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        character = self.initial["character"]
        self.fields["first_language"] = forms.ChoiceField(
            choices=_get_non_spoken_languages(character),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        self.fields["second_language"] = forms.ChoiceField(
            choices=_get_non_spoken_languages(character),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class SoldierForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tool_proficiency"] = forms.ChoiceField(
            choices=_get_gaming_set_tools(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class BackgroundForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        race = self.initial["race"]
        background = self.initial["background"]
        all_fields = {}
        all_fields["language"] = forms.ChoiceField(
            choices=_get_non_spoken_languages(race),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        all_fields["first_language"] = forms.ChoiceField(
            choices=_get_non_spoken_languages(race),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        all_fields["second_language"] = forms.ChoiceField(
            choices=_get_non_spoken_languages(race),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        all_fields["equipment"] = forms.ChoiceField(
            choices=_get_holy_symbols(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        all_fields["tool_proficiency"] = forms.ChoiceField(
            choices=_get_gaming_set_tools(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        match background:
            case Background.ACOLYTE:
                fields = ["first_language", "second_language", "equipment"]
            case Background.CRIMINAL:
                fields = ["tool_proficiency"]
            case Background.FOLK_HERO:
                fields = ["tool_proficiency", "equipment"]
            case Background.NOBLE:
                fields = ["language", "tool_proficiency"]
            case Background.SAGE:
                fields = ["first_language", "second_language"]
            case Background.SOLDIER:
                fields = ["tool_proficiency"]
        for field in fields:
            self.fields[field] = all_fields[field]
