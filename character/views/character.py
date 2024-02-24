from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView

from ..forms.character import CharacterCreateForm
from ..models.abilities import Ability, AbilityType
from ..models.character import Character
from ..models.equipment import Equipment, Inventory
from ..utils.builders import (
    Director,
    KlassBuilder,
    RaceBuilder,
)


class CharacterDetailView(LoginRequiredMixin, DetailView):
    model = Character
    template_name = "character/character.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inventory"] = Equipment.objects.filter(inventory=self.object.inventory)
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

    def _initialize_ability_scores(self, character, form):
        for ability_type in AbilityType.objects.all():
            ability = Ability.objects.create(
                ability_type=ability_type,
                score=form.cleaned_data[ability_type.get_name_display().lower()],
            )
            character.save()
            character.abilities.add(ability)

    def form_valid(self, form):
        character = form.save(commit=False)
        character.user = self.request.user

        self._initialize_ability_scores(character, form)
        race_builder = RaceBuilder(character)
        klass_builder = KlassBuilder(character)
        director = Director()
        director.build(race_builder, klass_builder)
        character.save()

        # Inventory
        character.inventory = Inventory.objects.create()

        return super().form_valid(form)
