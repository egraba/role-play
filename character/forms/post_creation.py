from django import forms

from character.models.classes import Class
from character.utils.classes import (
    get_armor_choices,
    get_gear_choices,
    get_pack_choices,
    get_weapon1_choices,
    get_weapon2_choices,
    get_weapon3_choices,
)


class SelectEquipmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        class_name = self.initial["class_name"]

        self.fields["weapon1"] = forms.ChoiceField(
            choices=get_weapon1_choices(class_name),
            label="First weapon",
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )

        if (
            class_name == Class.CLERIC
            or class_name == Class.FIGHTER
            or class_name == Class.ROGUE
        ):
            self.fields["weapon2"] = forms.ChoiceField(
                choices=get_weapon2_choices(class_name),
                label="Second weapon",
                widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
            )

        if class_name == Class.FIGHTER:
            self.fields["weapon3"] = forms.ChoiceField(
                choices=get_weapon3_choices(class_name),
                label="Third weapon",
                widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
            )

        if class_name == Class.CLERIC:
            self.fields["armor"] = forms.ChoiceField(
                choices=get_armor_choices(class_name),
                widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
            )

        if class_name == Class.WIZARD:
            self.fields["gear"] = forms.ChoiceField(
                choices=get_gear_choices(class_name),
                widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
            )

        self.fields["pack"] = forms.ChoiceField(
            choices=get_pack_choices(class_name),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
