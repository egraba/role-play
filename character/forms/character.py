from django import forms

from ..models.character import Character
from ..utils.abilities import AbilityScore


class CharacterCreateForm(forms.ModelForm):
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

    def clean(self):
        self.cleaned_data = super().clean()

        # The ability scores must be unique per ability.
        if len(self.cleaned_data) != len(set(self.cleaned_data.values())):
            raise forms.ValidationError("Each ability must have a different score...")
