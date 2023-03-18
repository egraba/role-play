from django import forms

from game.models import Damage, PendingAction, XpIncrease


class CreateGameForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput, max_length=50)
    description = forms.CharField(widget=forms.Textarea, max_length=1000)


class CreateTaleForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea, max_length=1000)


class CreatePendingActionForm(forms.ModelForm):
    class Meta:
        model = PendingAction
        fields = ["action_type"]


class IncreaseXpForm(forms.ModelForm):
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


class HealForm(forms.Form):
    hp = forms.IntegerField(min_value=1)


class ChoiceForm(forms.Form):
    selection = forms.CharField(widget=forms.Textarea, max_length=255)
