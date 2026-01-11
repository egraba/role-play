from django import forms

from ..constants.abilities import AbilityScore
from ..models.character import Character
from ..models.classes import Class
from .mixins import NoDuplicateValuesFormMixin


class CharacterCreateForm(NoDuplicateValuesFormMixin, forms.ModelForm):
    EMPTY_CHOICE = ("", "---------")

    klass = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        label="Class",
        empty_label="---------",
    )

    class Meta:
        model = Character
        fields = [
            "name",
            "species",
            "background",
        ]
        widgets = {
            "species": forms.Select(attrs={"class": "rpgui-dropdown"}),
            "background": forms.Select(attrs={"class": "rpgui-dropdown"}),
        }

    strength = forms.TypedChoiceField(
        choices=[EMPTY_CHOICE, *AbilityScore.choices],
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    dexterity = forms.TypedChoiceField(
        choices=[EMPTY_CHOICE, *AbilityScore.choices],
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    constitution = forms.TypedChoiceField(
        choices=[EMPTY_CHOICE, *AbilityScore.choices],
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    intelligence = forms.TypedChoiceField(
        choices=[EMPTY_CHOICE, *AbilityScore.choices],
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    wisdom = forms.TypedChoiceField(
        choices=[EMPTY_CHOICE, *AbilityScore.choices],
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    charisma = forms.TypedChoiceField(
        choices=[EMPTY_CHOICE, *AbilityScore.choices],
        coerce=int,
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
