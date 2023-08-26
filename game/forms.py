from django import forms

import game.models as gmodels


class CreateTaleForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, max_length=1000)


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
