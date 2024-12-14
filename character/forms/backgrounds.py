from django import forms

from ..constants.backgrounds import Background
from ..constants.equipment import GearType, ToolType
from ..constants.races import RACIAL_TRAITS, LanguageName, Race
from ..models.equipment import GearSettings, ToolSettings


def _get_non_spoken_languages(race: Race) -> set[tuple[str, str]]:
    """
    Return the set of language names without the languages spoken by the race given as parameter.
    """
    all_languages = LanguageName.choices
    race_languages = {
        (language.value, language.label)
        for language in RACIAL_TRAITS[race]["languages"]
    }
    return {
        (language[0], language[1])
        for language in all_languages
        if language not in race_languages
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
        all_fields["equipment_holy_symbols"] = forms.ChoiceField(
            choices=_get_holy_symbols(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        all_fields["equipment_artisans_tools"] = forms.ChoiceField(
            choices=_get_artisans_tools(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        all_fields["tool_proficiency_artisans_tools"] = forms.ChoiceField(
            choices=_get_artisans_tools(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        all_fields["tool_proficiency_gaming_set_tools"] = forms.ChoiceField(
            choices=_get_gaming_set_tools(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        match background:
            case Background.ACOLYTE:
                fields = ["first_language", "second_language", "equipment"]
                equipment_type = GearType.HOLY_SYMBOL
            case Background.CRIMINAL:
                fields = ["tool_proficiency"]
                tool_type = ToolType.GAMING_SET
            case Background.FOLK_HERO:
                fields = ["tool_proficiency", "equipment"]
                equipment_type = ToolType.ARTISANS_TOOLS
                tool_type = ToolType.ARTISANS_TOOLS
            case Background.NOBLE:
                fields = ["language", "tool_proficiency"]
                tool_type = ToolType.GAMING_SET
            case Background.SAGE:
                fields = ["first_language", "second_language"]
            case Background.SOLDIER:
                fields = ["tool_proficiency"]
                tool_type = ToolType.GAMING_SET
        for field in fields:
            if field == "equipment":
                match equipment_type:
                    case GearType.HOLY_SYMBOL:
                        self.fields[field] = all_fields["equipment_holy_symbols"]
                    case ToolType.ARTISANS_TOOLS:
                        self.fields[field] = all_fields["equipment_artisans_tools"]
            elif field == "tool_proficiency":
                match tool_type:
                    case ToolType.ARTISANS_TOOLS:
                        self.fields[field] = all_fields[
                            "tool_proficiency_artisans_tools"
                        ]
                    case ToolType.GAMING_SET:
                        self.fields[field] = all_fields[
                            "tool_proficiency_gaming_set_tools"
                        ]
            else:
                self.fields[field] = all_fields[field]
