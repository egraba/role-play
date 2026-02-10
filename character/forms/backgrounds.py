from django import forms

from ..constants.backgrounds import Background
from equipment.constants.equipment import GearType, ToolType
from equipment.models.equipment import GearSettings, ToolSettings


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
        background = self.initial["background"]

        holy_symbols_choices = self._get_choices(_get_holy_symbols())
        gaming_set_choices = self._get_choices(_get_gaming_set_tools())

        match background:
            case Background.ACOLYTE:
                self._add_field_if_choices("equipment", holy_symbols_choices)
            case Background.CRIMINAL:
                pass  # Thieves' Tools granted automatically
            case Background.SAGE:
                pass  # Calligrapher's Supplies granted automatically
            case Background.SOLDIER:
                self._add_field_if_choices("tool_proficiency", gaming_set_choices)
