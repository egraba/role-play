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
        """Return choices with empty choice prepended, or just empty choice if None."""
        return [self.EMPTY_CHOICE, *choices] if choices else [self.EMPTY_CHOICE]

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
        all_fields = {}
        all_fields["first_weapon"] = forms.ChoiceField(
            choices=self._get_choices(choices_provider.get_first_weapon_choices()),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        all_fields["second_weapon"] = forms.ChoiceField(
            choices=self._get_choices(choices_provider.get_second_weapon_choices()),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        all_fields["third_weapon"] = forms.ChoiceField(
            choices=self._get_choices(choices_provider.get_third_weapon_choices()),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        all_fields["armor"] = forms.ChoiceField(
            choices=self._get_choices(choices_provider.get_armor_choices()),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        all_fields["gear"] = forms.ChoiceField(
            choices=self._get_choices(choices_provider.get_gear_choices()),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        all_fields["pack"] = forms.ChoiceField(
            choices=self._get_choices(choices_provider.get_pack_choices()),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        for field in fields:
            self.fields[field] = all_fields[field]
