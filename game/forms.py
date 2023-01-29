from django import forms


class ChoiceForm(forms.Form):
    selection = forms.CharField(widget=forms.Textarea, max_length=255)


class NewGameForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput, max_length=255)
