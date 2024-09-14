from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView, ListView
from formtools.wizard.views import SessionWizardView

from ..forms.backgrounds import BackgroundForm
from ..forms.character import CharacterCreateForm
from ..forms.skills import SkillsSelectForm
from ..models.character import Character


class CharacterDetailView(LoginRequiredMixin, DetailView):
    model = Character
    template_name = "character/character.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inventory"] = self.object.inventory
        context["abilities"] = self.object.abilities.all()
        return context


class CharacterListView(LoginRequiredMixin, ListView):
    model = Character
    paginate_by = 20
    ordering = ["-xp"]
    template_name = "character/character_list.html"


class CharacterCreateView(LoginRequiredMixin, SessionWizardView):
    form_list = [CharacterCreateForm, SkillsSelectForm, BackgroundForm]
    template_name = "character/character_create.html"

    def get_form_initial(self, step):
        if step == "1":  # Skills selection
            data = self.storage.get_step_data("0")
            if data:
                klass = data.get("0-klass")
                return self.initial_dict.get(step, {"klass": klass})
        if step == "2":  # Background completion
            data = self.storage.get_step_data("0")
            if data:
                race = data.get("0-race")
                background = data.get("0-background")
                return self.initial_dict.get(
                    step, {"race": race, "background": background}
                )
        return self.initial_dict.get(step, {})

    def done(self, form_list, **kwargs):
        return HttpResponseRedirect(reverse("index"))
