from django import forms

import character.models as cmodels

ability_scores = [(15, 15), (14, 14), (13, 13), (12, 12), (10, 10), (8, 8)]


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
        choices=ability_scores,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    dexterity = forms.TypedChoiceField(
        choices=ability_scores,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    constitution = forms.TypedChoiceField(
        choices=ability_scores,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    intelligence = forms.TypedChoiceField(
        choices=ability_scores,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    wisdom = forms.TypedChoiceField(
        choices=ability_scores,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    charisma = forms.TypedChoiceField(
        choices=ability_scores,
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
