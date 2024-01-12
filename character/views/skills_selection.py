from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import FormView

from character.forms.skills_selection import ExtendedSkillsSelectForm, SkillsSelectForm
from character.models.character import Skill
from character.models.classes import Class
from utils.converters import duplicate_choice

from .mixins import CharacterContextMixin


class SkillsSelectView(LoginRequiredMixin, CharacterContextMixin, FormView):
    template_name = "character/skills_select.html"

    cleric_choices = {
        duplicate_choice(Skill.Name.HISTORY),
        duplicate_choice(Skill.Name.INSIGHT),
        duplicate_choice(Skill.Name.MEDICINE),
        duplicate_choice(Skill.Name.PERSUASION),
        duplicate_choice(Skill.Name.RELIGION),
    }

    fighter_choices = {
        duplicate_choice(Skill.Name.ACROBATICS),
        duplicate_choice(Skill.Name.ANIMAL_HANDLING),
        duplicate_choice(Skill.Name.ATHLETICS),
        duplicate_choice(Skill.Name.HISTORY),
        duplicate_choice(Skill.Name.INSIGHT),
        duplicate_choice(Skill.Name.INTIMIDATION),
        duplicate_choice(Skill.Name.PERCEPTION),
        duplicate_choice(Skill.Name.SURVIVAL),
    }

    rogue_choices = {
        duplicate_choice(Skill.Name.ACROBATICS),
        duplicate_choice(Skill.Name.ATHLETICS),
        duplicate_choice(Skill.Name.DECEPTION),
        duplicate_choice(Skill.Name.INSIGHT),
        duplicate_choice(Skill.Name.INTIMIDATION),
        duplicate_choice(Skill.Name.INVESTIGATION),
        duplicate_choice(Skill.Name.PERCEPTION),
        duplicate_choice(Skill.Name.PERFORMANCE),
        duplicate_choice(Skill.Name.PERSUASION),
        duplicate_choice(Skill.Name.SLEIGHT_OF_HAND),
        duplicate_choice(Skill.Name.STEALTH),
    }

    wizard_choices = {
        duplicate_choice(Skill.Name.ARCANA),
        duplicate_choice(Skill.Name.HISTORY),
        duplicate_choice(Skill.Name.INSIGHT),
        duplicate_choice(Skill.Name.INVESTIGATION),
        duplicate_choice(Skill.Name.MEDICINE),
        duplicate_choice(Skill.Name.RELIGION),
    }

    def get_success_url(self):
        return reverse("equipment-select", args=(self.character.id,))

    def get_form_class(self):
        match self.character.class_name:
            case Class.CLERIC:
                form_class = SkillsSelectForm
            case Class.FIGHTER:
                form_class = ExtendedSkillsSelectForm
            case Class.ROGUE:
                form_class = SkillsSelectForm
            case Class.WIZARD:
                form_class = SkillsSelectForm
        return form_class

    def get_initial(self):
        initial = {}
        match self.character.class_name:
            case Class.CLERIC:
                initial["choices"] = self.cleric_choices
            case Class.FIGHTER:
                initial["choices"] = self.fighter_choices
            case Class.ROGUE:
                initial["choices"] = self.rogue_choices
            case Class.WIZARD:
                initial["choices"] = self.wizard_choices
        return initial
