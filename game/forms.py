from django import forms


class NewGameForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput, max_length=50)


class CreateTaleForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea, max_length=1000)


class ChoiceForm(forms.Form):
    selection = forms.CharField(widget=forms.Textarea, max_length=255)
