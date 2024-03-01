from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import FormView

from ..forms.skills import ExtendedSkillsSelectForm, SkillsSelectForm
from ..models.klasses import Klass
from ..utils.proficiencies import get_skills
from .mixins import CharacterContextMixin


class SkillsSelectView(LoginRequiredMixin, CharacterContextMixin, FormView):
    template_name = "character/skills_select.html"

    def get_success_url(self):
        return reverse("equipment-select", args=(self.character.id,))

    def get_form_class(self):
        match self.character.class_name:
            case Klass.CLERIC:
                form_class = SkillsSelectForm
            case Klass.FIGHTER:
                form_class = SkillsSelectForm
            case Klass.ROGUE:
                form_class = ExtendedSkillsSelectForm
            case Klass.WIZARD:
                form_class = SkillsSelectForm
        return form_class

    def get_initial(self):
        initial = {}
        match self.character.class_name:
            case Klass.CLERIC:
                initial["choices"] = get_skills(Klass.CLERIC)
            case Klass.FIGHTER:
                initial["choices"] = get_skills(Klass.FIGHTER)
            case Klass.ROGUE:
                initial["choices"] = get_skills(Klass.ROGUE)
            case Klass.WIZARD:
                initial["choices"] = get_skills(Klass.WIZARD)
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
