from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import FormView

from .mixins import CharacterContextMixin


class SkillsSelectView(LoginRequiredMixin, CharacterContextMixin, FormView):
    template_name = "character/skills_select.html"

    def get_success_url(self):
        return reverse("background-complete", args=(self.character.id,))

    def get_initial(self):
        return {"klass": self.character.klass}

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
