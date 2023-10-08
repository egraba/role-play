from django import forms

import character.abilities as abilities
from character.models.character import Character


class CreateCharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = [
            "name",
            "race",
            "class_name",
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        ]
        widgets = {
            "race": forms.Select(attrs={"class": "rpgui-dropdown"}),
            "class_name": forms.Select(attrs={"class": "rpgui-dropdown"}),
        }

    strength = forms.TypedChoiceField(
        choices=abilities.scores,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    dexterity = forms.TypedChoiceField(
        choices=abilities.scores,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    constitution = forms.TypedChoiceField(
        choices=abilities.scores,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    intelligence = forms.TypedChoiceField(
        choices=abilities.scores,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    wisdom = forms.TypedChoiceField(
        choices=abilities.scores,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    charisma = forms.TypedChoiceField(
        choices=abilities.scores,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )

    def clean(self):
        self.cleaned_data = super().clean()
        # The ability scores must be unique per ability.
        if len(self.cleaned_data) != len(set(self.cleaned_data.values())):
            raise forms.ValidationError("Each ability must have a different score...")
        pass


class ChoseEquipmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            weapon_list = self.initial["weapon_list"]
            armor_list = self.initial["armor_list"]
            pack_list = self.initial["pack_list"]
        except KeyError:
            raise forms.ValidationError(
                "An error occurred retrieving available equipment..."
            )
        self.fields["weapon"] = forms.ChoiceField(
            choices=weapon_list,
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        self.fields["armor"] = forms.ChoiceField(
            choices=armor_list,
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        self.fields["pack"] = forms.ChoiceField(
            choices=pack_list,
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
