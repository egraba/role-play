from django import forms

from ..constants.klasses import Klass
from .equipment_choices_providers import (
    ClericEquipmentChoicesProvider,
    FighterEquipmentChoicesProvider,
    RogueEquipmentChoicesProvider,
    WizardEquipmentChoicesProvider,
)


class EquipmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        klass = self.initial["klass"]
        match klass:
            case Klass.CLERIC:
                provider = ClericEquipmentChoicesProvider()
                fields = ["first_weapon", "second_weapon", "armor", "gear", "pack"]
            case Klass.FIGHTER:
                provider = FighterEquipmentChoicesProvider()
                fields = ["first_weapon", "second_weapon", "third_weapon", "pack"]
            case Klass.ROGUE:
                provider = RogueEquipmentChoicesProvider()
                fields = ["first_weapon", "second_weapon", "pack"]
            case Klass.WIZARD:
                provider = WizardEquipmentChoicesProvider()
                fields = ["first_weapon", "gear", "pack"]
        all_fields = {}
        all_fields["first_weapon"] = forms.ChoiceField(
            choices=provider.get_first_weapon_choices(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        all_fields["second_weapon"] = forms.ChoiceField(
            choices=provider.get_second_weapon_choices(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        all_fields["third_weapon"] = forms.ChoiceField(
            choices=provider.get_third_weapon_choices(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        all_fields["armor"] = forms.ChoiceField(
            choices=provider.get_armor_choices(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        all_fields["gear"] = forms.ChoiceField(
            choices=provider.get_gear_choices(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        all_fields["pack"] = forms.ChoiceField(
            choices=provider.get_pack_choices(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        for field in fields:
            self.fields[field] = all_fields[field]
