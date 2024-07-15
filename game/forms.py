from django import forms

from character.constants.abilities import AbilityName
from character.models.character import Character

from .models.events import RollRequest
from .constants.combat import FighterAttributeChoices


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
        self.fields["ability_type"].choices = AbilityName.choices


class CombatCreateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        game = self.initial["game"]
        characters = Character.objects.filter(player__game=game)
        for character in characters:
            self.fields[character.name] = forms.MultipleChoiceField(
                required=False,
                widget=forms.CheckboxSelectMultiple,
                choices=FighterAttributeChoices,
            )

    def clean(self):
        self.cleaned_data = super().clean()
        if not any(
            FighterAttributeChoices.IS_FIGHTING in value
            for value in self.cleaned_data.values()
        ):
            raise forms.ValidationError("A combat should have at least one fighter")
