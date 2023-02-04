from django import forms


class NewGameForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput, max_length=255)


class NewNarrativeForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, max_length=1024)


class ChoiceForm(forms.Form):
    selection = forms.CharField(widget=forms.Textarea, max_length=255)
