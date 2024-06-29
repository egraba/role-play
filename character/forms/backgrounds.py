from django import forms

from ..constants.equipment import GearType, ToolType
from ..models.character import Character
from ..models.equipment import GearSettings, ToolSettings
from ..models.races import Language
from .mixins import DuplicateValuesMixin


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
        for gear in GearSettings.objects.filter(gear_type=GearType.HOLY_SYMBOL)
    }


def get_gaming_set_tools() -> set[tuple[str, str]]:
    """
    Return the set of gaming set tools names.
    """
    return {
        (tool.name, tool.get_name_display())
        for tool in ToolSettings.objects.filter(tool_type=ToolType.GAMING_SET)
    }


def get_artisans_tools() -> set[tuple[str, str]]:
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
            choices=get_non_spoken_languages(character),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        self.fields["second_language"] = forms.ChoiceField(
            choices=get_non_spoken_languages(character),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        self.fields["equipment"] = forms.ChoiceField(
            choices=get_holy_symbols(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class CriminalForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tool_proficiency"] = forms.ChoiceField(
            choices=get_gaming_set_tools(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class FolkHeroForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tool_proficiency"] = forms.ChoiceField(
            choices=get_artisans_tools(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        self.fields["equipment"] = forms.ChoiceField(
            choices=get_artisans_tools(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class NobleForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        character = self.initial["character"]
        self.fields["language"] = forms.ChoiceField(
            choices=get_non_spoken_languages(character),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        self.fields["tool_proficiency"] = forms.ChoiceField(
            choices=get_gaming_set_tools(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class SageForm(DuplicateValuesMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        character = self.initial["character"]
        self.fields["first_language"] = forms.ChoiceField(
            choices=get_non_spoken_languages(character),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        self.fields["second_language"] = forms.ChoiceField(
            choices=get_non_spoken_languages(character),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class SoldierForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tool_proficiency"] = forms.ChoiceField(
            choices=get_gaming_set_tools(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
