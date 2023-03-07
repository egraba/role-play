from django import forms

from game.models import PendingAction


class CreateGameForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput, max_length=50)
    description = forms.CharField(widget=forms.Textarea, max_length=1000)


class CreateTaleForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea, max_length=1000)


class CreatePendingActionForm(forms.ModelForm):
    class Meta:
        model = PendingAction
        fields = ["action_type"]


class ChoiceForm(forms.Form):
    selection = forms.CharField(widget=forms.Textarea, max_length=255)
