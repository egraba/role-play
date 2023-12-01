from django import forms
from django.db import models

from character.models.character import Character
from character.utils.abilities import AbilityScore


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
    class Weapon(models.TextChoices):
        MACE = "Mace"
        WARHAMMER = "warhammer"

    class Armor(models.TextChoices):
        SCALE_MAIL = "Scale mail"
        LEATHER_ARMOR = "Leather armor"
        CHAIN_MAIL = "chain mail"

    weapon = forms.ChoiceField(
        choices=Weapon.choices, widget=forms.Select(attrs={"class": "rpgui-dropdown"})
    )
    armor = forms.ChoiceField(
        choices=Armor.choices, widget=forms.Select(attrs={"class": "rpgui-dropdown"})
    )
