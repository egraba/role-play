from django import forms

from game.models import Choice, Damage, DiceLaunch, Healing, XpIncrease


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


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ["selection"]
        widgets = {
            "selection": forms.Textarea,
        }
