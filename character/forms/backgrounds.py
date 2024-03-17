from django import forms
from .mixins import DuplicateValuesMixin


class AcolyteForm(DuplicateValuesMixin):
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


class SageForm(DuplicateValuesMixin):
    first_language = forms.ChoiceField()
    second_language = forms.ChoiceField()


class SoldierForm(forms.Form):
    tool_proficiency = forms.ChoiceField()
