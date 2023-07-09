from django import forms

import character.models as cmodels


class CreateCharacterForm(forms.ModelForm):
    class Meta:
        model = cmodels.Character
        fields = ["name", "race"]
        widgets = {
            "race": forms.Select(attrs={"class": "rpgui-dropdown"}),
        }
