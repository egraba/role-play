from django import forms

from utils.converters import duplicate_choice

from ..constants.classes import ClassName
from ..constants.skills import SkillName
from .mixins import NoDuplicateValuesFormMixin


def _get_skills(class_name: str) -> set[tuple[str, str]] | None:
    match class_name:
        case ClassName.CLERIC:
            return {
                duplicate_choice(SkillName.HISTORY),
                duplicate_choice(SkillName.INSIGHT),
                duplicate_choice(SkillName.MEDICINE),
                duplicate_choice(SkillName.PERSUASION),
                duplicate_choice(SkillName.RELIGION),
            }
        case ClassName.FIGHTER:
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
        case ClassName.ROGUE:
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
        case ClassName.WIZARD:
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

    def _get_choices(self, choices):
        """Return choices with empty choice prepended, or None if no choices."""
        return [self.EMPTY_CHOICE, *choices] if choices else None

    def _add_field_if_choices(self, field_name, choices):
        """Add field only if there are choices available."""
        if choices:
            self.fields[field_name] = forms.ChoiceField(
                choices=choices,
                widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        klass = self.initial.get("klass")
        # klass can be a Class model instance or a ClassName enum/string value
        # Use hasattr for _meta to detect Django model instances
        class_name = klass.name if hasattr(klass, "_meta") else klass
        choices = self._get_choices(_get_skills(class_name))

        self._add_field_if_choices("first_skill", choices)
        self._add_field_if_choices("second_skill", choices)
        if class_name == ClassName.ROGUE:
            self._add_field_if_choices("third_skill", choices)
            self._add_field_if_choices("fourth_skill", choices)
