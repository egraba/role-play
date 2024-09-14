from django import forms

from utils.converters import duplicate_choice

from ..constants.klasses import Klass
from ..constants.skills import SkillName


def _get_skills(klass: Klass) -> set[tuple[str, str]] | None:
    match klass:
        case Klass.CLERIC:
            return {
                duplicate_choice(SkillName.HISTORY),
                duplicate_choice(SkillName.INSIGHT),
                duplicate_choice(SkillName.MEDICINE),
                duplicate_choice(SkillName.PERSUASION),
                duplicate_choice(SkillName.RELIGION),
            }
        case Klass.FIGHTER:
            return {
                duplicate_choice(SkillName.ACROBATICS),
                duplicate_choice(SkillName.ANIMAL_HANDLING),
                duplicate_choice(SkillName.ATHLETICS),
                duplicate_choice(SkillName.HISTORY),
                duplicate_choice(SkillName.INSIGHT),
                duplicate_choice(SkillName.INTIMIDATION),
                duplicate_choice(SkillName.PERCEPTION),
                duplicate_choice(SkillName.SURVIVAL),
            }
        case Klass.ROGUE:
            return {
                duplicate_choice(SkillName.ACROBATICS),
                duplicate_choice(SkillName.ATHLETICS),
                duplicate_choice(SkillName.DECEPTION),
                duplicate_choice(SkillName.INSIGHT),
                duplicate_choice(SkillName.INTIMIDATION),
                duplicate_choice(SkillName.INVESTIGATION),
                duplicate_choice(SkillName.PERCEPTION),
                duplicate_choice(SkillName.PERFORMANCE),
                duplicate_choice(SkillName.PERSUASION),
                duplicate_choice(SkillName.SLEIGHT_OF_HAND),
                duplicate_choice(SkillName.STEALTH),
            }
        case Klass.WIZARD:
            return {
                duplicate_choice(SkillName.ARCANA),
                duplicate_choice(SkillName.HISTORY),
                duplicate_choice(SkillName.INSIGHT),
                duplicate_choice(SkillName.INVESTIGATION),
                duplicate_choice(SkillName.MEDICINE),
                duplicate_choice(SkillName.RELIGION),
            }
        case _:
            return None


class SkillsSelectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        klass = self.initial["klass"]
        self.fields["first_skill"] = forms.ChoiceField(
            choices=_get_skills(klass),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        self.fields["second_skill"] = forms.ChoiceField(
            choices=_get_skills(klass),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        if klass == Klass.ROGUE:
            self.fields["third_skill"] = forms.ChoiceField(
                choices=_get_skills(klass),
                widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
            )
            self.fields["fourth_skill"] = forms.ChoiceField(
                choices=_get_skills(klass),
                widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
            )

    def clean(self):
        self.cleaned_data = super().clean()
        if len(self.cleaned_data) != len(set(self.cleaned_data.values())):
            raise forms.ValidationError("The selected skills must be unique...")


class ExtendedSkillsSelectForm(SkillsSelectForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        klass = self.initial["klass"]
        self.fields["third_skill"] = forms.ChoiceField(
            choices=_get_skills(klass),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        self.fields["fourth_skill"] = forms.ChoiceField(
            choices=_get_skills(klass),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
