from django import forms

from utils.converters import duplicate_choice

from ..constants.klasses import Klass
from ..constants.skills import SkillName
from .mixins import NoDuplicateValuesFormMixin


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


class SkillsSelectForm(NoDuplicateValuesFormMixin, forms.Form):
    EMPTY_CHOICE = ("", "---------")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        klass = self.initial["klass"]
        choices = [self.EMPTY_CHOICE, *_get_skills(klass)]
        self.fields["first_skill"] = forms.ChoiceField(
            choices=choices,
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        self.fields["second_skill"] = forms.ChoiceField(
            choices=choices,
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )
        if klass == Klass.ROGUE:
            self.fields["third_skill"] = forms.ChoiceField(
                choices=choices,
                widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
            )
            self.fields["fourth_skill"] = forms.ChoiceField(
                choices=choices,
                widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
            )
