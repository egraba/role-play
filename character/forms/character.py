from django import forms

from ..constants.abilities import AbilityScore
from ..models.character import Character
from .mixins import NoDuplicateValuesFormMixin


class CharacterCreateForm(NoDuplicateValuesFormMixin, forms.ModelForm):
    class Meta:
        model = Character
        fields = [
            "name",
            "race",
            "klass",
            "background",
        ]
        widgets = {
            "race": forms.Select(attrs={"class": "rpgui-dropdown"}),
            "klass": forms.Select(attrs={"class": "rpgui-dropdown"}),
            "background": forms.Select(attrs={"class": "rpgui-dropdown"}),
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
