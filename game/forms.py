from django import forms

from character.models.abilities import AbilityType
from character.models.character import Character

from .models.events import RollRequest


class QuestCreateForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, max_length=1000)


class AbilityCheckRequestForm(forms.ModelForm):
    class Meta:
        model = RollRequest
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
        self.fields["ability_type"].choices = AbilityType.AbilityName.choices


class CombatCreateForm(forms.Form):
    pass
