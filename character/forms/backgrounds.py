from django import forms


class AcolyteForm(forms.Form):
    first_language = forms.ChoiceField()
    second_language = forms.ChoiceField()
    equipment = forms.ChoiceField()


class CriminalForm(forms.Form):
    tool_proficiency = forms.ChoiceField()


class FolkHeroForm(forms.Form):
    tool_proficiency = forms.ChoiceField()
    equipment = forms.ChoiceField()


class NobleForm(forms.Form):
    tool_proficiency = forms.ChoiceField()
    language = forms.ChoiceField()


class SageForm(forms.Form):
    first_language = forms.ChoiceField()
    second_language = forms.ChoiceField()


class SoldierForm(forms.Form):
    tool_proficiency = forms.ChoiceField()
