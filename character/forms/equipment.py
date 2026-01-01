from django import forms

from ..constants.klasses import Klass
from .equipment_choices_providers import (
    ClericEquipmentChoicesProvider,
    FighterEquipmentChoicesProvider,
    RogueEquipmentChoicesProvider,
    WizardEquipmentChoicesProvider,
)


class EquipmentSelectForm(forms.Form):
    EMPTY_CHOICE = ("", "---------")

    def _get_choices(self, choices):
        """Return choices with empty choice prepended, or None if no choices."""
        return [self.EMPTY_CHOICE, *choices] if choices else None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        klass = self.initial["klass"]
        match klass:
            case Klass.CLERIC:
                choices_provider = ClericEquipmentChoicesProvider()
                fields = ["first_weapon", "second_weapon", "armor", "gear", "pack"]
            case Klass.FIGHTER:
                choices_provider = FighterEquipmentChoicesProvider()
                fields = ["first_weapon", "second_weapon", "third_weapon", "pack"]
            case Klass.ROGUE:
                choices_provider = RogueEquipmentChoicesProvider()
                fields = ["first_weapon", "second_weapon", "pack"]
            case Klass.WIZARD:
                choices_provider = WizardEquipmentChoicesProvider()
                fields = ["first_weapon", "gear", "pack"]

        field_choices = {
            "first_weapon": self._get_choices(
                choices_provider.get_first_weapon_choices()
            ),
            "second_weapon": self._get_choices(
                choices_provider.get_second_weapon_choices()
            ),
            "third_weapon": self._get_choices(
                choices_provider.get_third_weapon_choices()
            ),
            "armor": self._get_choices(choices_provider.get_armor_choices()),
            "gear": self._get_choices(choices_provider.get_gear_choices()),
            "pack": self._get_choices(choices_provider.get_pack_choices()),
        }

        for field in fields:
            choices = field_choices[field]
            if choices:
                self.fields[field] = forms.ChoiceField(
                    choices=choices,
                    widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
                )
