from django import forms

from ..utils.backgrounds import (
    get_artisans_tools,
    get_gaming_set_tools,
    get_holy_symbols,
    get_non_spoken_languages,
)
from .mixins import DuplicateValuesMixin


class AcolyteForm(DuplicateValuesMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        character = self.initial["character"]

        self.fields["first_language"] = forms.ChoiceField(
            choices=get_non_spoken_languages(character),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )

        self.fields["second_language"] = forms.ChoiceField(
            choices=get_non_spoken_languages(character),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )

        self.fields["equipment"] = forms.ChoiceField(
            choices=get_holy_symbols(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class CriminalForm(forms.Form):
    tool_proficiency = forms.ChoiceField(
        choices=get_gaming_set_tools(),
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )


class FolkHeroForm(forms.Form):
    tool_proficiency = forms.ChoiceField(
        choices=get_artisans_tools(),
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
    equipment = forms.ChoiceField(
        choices=get_artisans_tools(),
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )


class NobleForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        character = self.initial["character"]

        self.fields["language"] = forms.ChoiceField(
            choices=get_non_spoken_languages(character),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )

    tool_proficiency = forms.ChoiceField(
        choices=get_gaming_set_tools(),
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )


class SageForm(DuplicateValuesMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        character = self.initial["character"]

        self.fields["first_language"] = forms.ChoiceField(
            choices=get_non_spoken_languages(character),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )

        self.fields["second_language"] = forms.ChoiceField(
            choices=get_non_spoken_languages(character),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class SoldierForm(forms.Form):
    tool_proficiency = forms.ChoiceField(
        choices=get_gaming_set_tools(),
        widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
    )
