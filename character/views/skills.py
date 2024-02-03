from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import FormView

from ..forms.skills import ExtendedSkillsSelectForm, SkillsSelectForm
from ..models.classes import Class
from ..utils.skills import (
    cleric_choices,
    fighter_choices,
    rogue_choices,
    wizard_choices,
)
from .mixins import CharacterContextMixin


class SkillsSelectView(LoginRequiredMixin, CharacterContextMixin, FormView):
    template_name = "character/skills_select.html"

    def get_success_url(self):
        return reverse("equipment-select", args=(self.character.id,))

    def get_form_class(self):
        match self.character.class_name:
            case Class.CLERIC:
                form_class = SkillsSelectForm
            case Class.FIGHTER:
                form_class = SkillsSelectForm
            case Class.ROGUE:
                form_class = ExtendedSkillsSelectForm
            case Class.WIZARD:
                form_class = SkillsSelectForm
        return form_class

    def get_initial(self):
        initial = {}
        match self.character.class_name:
            case Class.CLERIC:
                initial["choices"] = cleric_choices
            case Class.FIGHTER:
                initial["choices"] = fighter_choices
            case Class.ROGUE:
                initial["choices"] = rogue_choices
            case Class.WIZARD:
                initial["choices"] = wizard_choices
        return initial

    def form_valid(self, form):
        first_skill = form.cleaned_data["first_skill"]
        self.character.skills.add(first_skill)

        second_skill = form.cleaned_data["second_skill"]
        self.character.skills.add(second_skill)

        try:
            third_skill = form.cleaned_data["third_skill"]
            self.character.skills.add(third_skill)
        except KeyError:
            pass

        try:
            fourth_skill = form.cleaned_data["fourth_skill"]
            self.character.skills.add(fourth_skill)
        except KeyError:
            pass

        return super().form_valid(form)
