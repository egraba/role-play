from django import forms

import game.models as gmodels


class CreateGameForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput, max_length=50)
    description = forms.CharField(widget=forms.Textarea, max_length=1000)

    def clean_name(self):
        name = self.cleaned_data["name"]
        if gmodels.Game.objects.filter(name=name).exists():
            raise forms.ValidationError(
                "A game with the same name already exists... Please find another name."
            )
        return name


class CreateTaleForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, max_length=1000)


class CreatePendingActionForm(forms.ModelForm):
    class Meta:
        model = gmodels.PendingAction
        fields = ["action_type"]
        widgets = {
            "action_type": forms.Select(attrs={"class": "rpgui-dropdown"}),
        }


class IncreaseXpForm(forms.ModelForm):
    class Meta:
        model = gmodels.XpIncrease
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
        model = gmodels.Damage
        fields = ["hp"]

    def clean_hp(self):
        hp = self.cleaned_data["hp"]
        if hp < 1:
            raise forms.ValidationError("The damage should be superior to 1...")
        return hp


class HealForm(forms.ModelForm):
    class Meta:
        model = gmodels.Healing
        fields = ["hp"]

    def clean_hp(self):
        hp = self.cleaned_data["hp"]
        if hp < 1:
            raise forms.ValidationError("The damage should be superior to 1...")
        return hp


class CreateCharacterForm(forms.ModelForm):
    class Meta:
        model = gmodels.Character
        fields = ["name", "race"]
        widgets = {
            "race": forms.Select(attrs={"class": "rpgui-dropdown"}),
        }


class DiceLaunchForm(forms.ModelForm):
    class Meta:
        model = gmodels.DiceLaunch
        fields = []


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = gmodels.Choice
        fields = ["selection"]
        widgets = {
            "selection": forms.Textarea,
        }
