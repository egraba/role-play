from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView

from ..character_builder import (
    build_character,
)
from ..flows import CreationFlow
from ..forms.character import CharacterCreateForm
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


class CharacterCreateView(LoginRequiredMixin, CreateView):
    model = Character
    form_class = CharacterCreateForm
    template_name = "character/character_create.html"

    def get_success_url(self):
        return reverse("skills-select", args=(self.object.id,))

    def form_valid(self, form):
        character = form.save(commit=False)
        character.user = self.request.user
        build_character(character, form)
        CreationFlow(character).select_skills()
        return super().form_valid(form)
