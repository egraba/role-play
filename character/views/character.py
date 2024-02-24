from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView

from ..forms.character import CharacterCreateForm
from ..models.abilities import Ability, AbilityType
from ..models.character import Character
from ..models.classes import Class
from ..models.equipment import Equipment, Inventory
from ..models.proficiencies import SavingThrowProficiency
from ..models.races import Race
from ..utils.proficiencies import get_saving_throws
from ..utils.builders import (
    DwarfBuilder,
    ElfBuilder,
    HalflingBuilder,
    HumanBuilder,
    Director,
    ClericBuilder,
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

    def _apply_class_features(self, character, class_feature):
        character.hit_dice = class_feature.hitpoints.hit_dice
        character.hp += class_feature.hitpoints.hp_first_level
        constitution_modifier = character.abilities.get(
            ability_type=AbilityType.Name.CONSTITUTION
        ).modifier
        character.hp += constitution_modifier
        character.max_hp = character.hp
        character.hp_increase = class_feature.hitpoints.hp_higher_levels
        saving_throws = get_saving_throws(class_feature.class_name)
        for ability in saving_throws:
            SavingThrowProficiency.objects.create(
                character=character, ability_type=AbilityType.objects.get(name=ability)
            )

    def form_valid(self, form):
        character = form.save(commit=False)
        character.user = self.request.user
        self._initialize_ability_scores(character, form)

        # Racial traits
        match character.race:
            case Race.DWARF:
                race_builder = DwarfBuilder(character)
            case Race.ELF:
                race_builder = ElfBuilder(character)
            case Race.HALFLING:
                race_builder = HalflingBuilder(character)
            case Race.HUMAN:
                race_builder = HumanBuilder(character)
            case _:
                race_builder = DwarfBuilder(character)

        # Class features
        match character.class_name:
            case Class.CLERIC:
                klass_builder = ClericBuilder(character)
            case _:
                klass_builder = ClericBuilder(character)

        director = Director()
        director.build(race_builder, klass_builder)

        character.save()

        # Inventory
        character.inventory = Inventory.objects.create()

        return super().form_valid(form)
