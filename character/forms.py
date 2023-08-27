from django import forms

import character.abilities as abilities
import character.models as cmodels


class CreateCharacterForm(forms.ModelForm):
    class Meta:
        model = cmodels.Character
        fields = [
            "name",
            "race",
            "class_name",
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
        cleaned_data = super().clean()
        # The ability scores must be unique per ability.
        if len(cleaned_data) != len(set(cleaned_data.values())):
            raise forms.ValidationError("Each ability must have a different score...")
        pass
