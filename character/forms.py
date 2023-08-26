from django import forms

import character.models as cmodels


class CreateCharacterForm(forms.ModelForm):
    class Meta:
        model = cmodels.Character
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
