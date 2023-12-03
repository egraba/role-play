from django import forms

from character.models.classes import Class
from character.utils.classes.equipment_choices import (
    ClericEquipmentChoicesProvider,
    FighterEquipmentChoicesProvider,
    RogueEquipmentChoicesProvider,
    WizardEquipmentChoicesProvider,
)


class SelectEquipmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        class_name = self.initial["class_name"]
        match class_name:
            case Class.CLERIC:
                equipment_provider = ClericEquipmentChoicesProvider()
            case Class.FIGHTER:
                equipment_provider = FighterEquipmentChoicesProvider()
            case Class.ROGUE:
                equipment_provider = RogueEquipmentChoicesProvider()
            case Class.WIZARD:
                equipment_provider = WizardEquipmentChoicesProvider()

        self.fields["weapon1"] = forms.ChoiceField(
            choices=equipment_provider.get_weapon1_choices(),
            label="First weapon",
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )

        if (
            class_name == Class.CLERIC
            or class_name == Class.FIGHTER
            or class_name == Class.ROGUE
        ):
            self.fields["weapon2"] = forms.ChoiceField(
                choices=equipment_provider.get_weapon2_choices(),
                label="Second weapon",
                widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
            )

        if class_name == Class.FIGHTER:
            self.fields["weapon3"] = forms.ChoiceField(
                choices=equipment_provider.get_weapon3_choices(),
                label="Third weapon",
                widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
            )

        if class_name == Class.CLERIC:
            self.fields["armor"] = forms.ChoiceField(
                choices=equipment_provider.get_armor_choices(),
                widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
            )

        if class_name == Class.CLERIC or class_name == Class.WIZARD:
            self.fields["gear"] = forms.ChoiceField(
                choices=equipment_provider.get_gear_choices(),
                widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
            )

        self.fields["pack"] = forms.ChoiceField(
            choices=equipment_provider.get_pack_choices(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
