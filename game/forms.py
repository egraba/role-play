from django import forms

from character.models.abilities import AbilityType
from character.models.character import Character
from game.models.events import (
    AbilityCheckRequest,
    Damage,
    DiceLaunch,
    Healing,
    XpIncrease,
)


class QuestCreateForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, max_length=1000)


class XpIncreaseForm(forms.ModelForm):
    class Meta:
        model = XpIncrease
        fields = ["xp"]

    def clean_xp(self):
        xp = self.cleaned_data["xp"]
        if xp < 1:
            raise forms.ValidationError(
                "The gained experience should be superior to 1..."
            )
        return xp


class DamageForm(forms.ModelForm):
    class Meta:
        model = Damage
        fields = ["hp"]

    def clean_hp(self):
        hp = self.cleaned_data["hp"]
        if hp < 1:
            raise forms.ValidationError("The damage should be superior to 1...")
        return hp


class HealingForm(forms.ModelForm):
    class Meta:
        model = Healing
        fields = ["hp"]

    def clean_hp(self):
        hp = self.cleaned_data["hp"]
        if hp < 1:
            raise forms.ValidationError("The damage should be superior to 1...")
        return hp


class DiceLaunchForm(forms.ModelForm):
    class Meta:
        model = DiceLaunch
        fields = []


class AbilityCheckRequestForm(forms.ModelForm):
    class Meta:
        model = AbilityCheckRequest
        fields = ["character", "ability_type", "difficulty_class"]
        widgets = {
            "ability_type": forms.Select(attrs={"class": "rpgui-dropdown"}),
            "difficulty_class": forms.Select(attrs={"class": "rpgui-dropdown"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        game = self.initial["game"]

        self.fields["character"] = forms.ModelChoiceField(
            queryset=Character.objects.filter(player__game=game),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )

        self.fields["ability_type"].label = "Ability"
        self.fields["ability_type"].choices = AbilityType.Name.choices
