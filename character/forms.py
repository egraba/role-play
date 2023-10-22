from django import forms

from character.models.character import Character
from character.utils.abilities import AbilityScore
from character.utils.classes import get_armor_choices, get_weapon_choices


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
        choices=AbilityScore.choices,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    dexterity = forms.TypedChoiceField(
        choices=AbilityScore.choices,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    constitution = forms.TypedChoiceField(
        choices=AbilityScore.choices,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    intelligence = forms.TypedChoiceField(
        choices=AbilityScore.choices,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    wisdom = forms.TypedChoiceField(
        choices=AbilityScore.choices,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    charisma = forms.TypedChoiceField(
        choices=AbilityScore.choices,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )

    def clean(self):
        self.cleaned_data = super().clean()
        # The ability scores must be unique per ability.
        if len(self.cleaned_data) != len(set(self.cleaned_data.values())):
            raise forms.ValidationError("Each ability must have a different score...")
        pass


class SelectEquipmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        class_name = self.initial["class_name"]

        self.fields["weapon"] = forms.ChoiceField(
            choices=get_weapon_choices(class_name),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )

        self.fields["armor"] = forms.ChoiceField(
            choices=get_armor_choices(class_name),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )

        """self.fields["pack"] = forms.ChoiceField(
            choices=pack_list,
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )

        self.fields["gear"] = forms.ChoiceField(
            choices=gear_list,
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )"""
