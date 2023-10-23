from django import forms

from character.utils.classes import (
    get_armor_choices,
    get_pack_choices,
    get_weapon_choices,
)


class SelectEquipmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        class_name = self.initial["class_name"]

        self.fields["weapon1"] = forms.ChoiceField(
            choices=get_weapon_choices(class_name),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )

        self.fields["armor"] = forms.ChoiceField(
            choices=get_armor_choices(class_name),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )

        self.fields["weapon2"] = forms.ChoiceField(
            choices=get_weapon_choices(class_name),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )

        self.fields["pack"] = forms.ChoiceField(
            choices=get_pack_choices(class_name),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
