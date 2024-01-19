from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView

from character.forms.character import CharacterCreateForm
from character.models.character import (
    Ability,
    AbilityScoreIncrease,
    AbilityType,
    Character,
)
from character.models.classes import ClassAdvancement, ClassFeature, Proficiencies
from character.models.equipment import Equipment, Inventory
from character.models.races import RacialTrait
from character.utils.abilities import compute_ability_modifier


class CharacterDetailView(LoginRequiredMixin, DetailView):
    model = Character
    template_name = "character/character.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inventory"] = Equipment.objects.filter(inventory=self.object.inventory)
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

    def _apply_racial_traits(self, character, racial_trait):
        character.adult_age = racial_trait.adult_age
        character.life_expectancy = racial_trait.life_expectancy
        character.alignment = racial_trait.alignment
        character.size = racial_trait.size
        character.speed = racial_trait.speed
        # Need to save before setting many-to-many relationships
        character.save()
        character.languages.set(racial_trait.languages.all())
        character.senses.set(racial_trait.senses.all())

    def _apply_ability_score_increases(self, character, racial_trait):
        ability_score_increases = AbilityScoreIncrease.objects.filter(
            racial_trait__race=racial_trait.race
        )
        if ability_score_increases is not None:
            for i in ability_score_increases:
                ability = character.abilities.get(ability_type=i.ability)
                ability.score += i.increase
                ability.save()

    def _compute_ability_modifiers(self, character):
        for ability in character.abilities.all():
            ability.modifier = compute_ability_modifier(ability.score)

    def _apply_class_advancement(self, character, level):
        class_advancement = ClassAdvancement.objects.get(
            class_name=character.class_name, level=1
        )
        character.proficiency_bonus += class_advancement.proficiency_bonus

    def _apply_class_features(self, character, class_feature):
        character.hit_dice = class_feature.hitpoints.hit_dice
        character.hp += class_feature.hitpoints.hp_first_level
        constitution_modifier = character.abilities.get(
            ability_type=AbilityType.Name.CONSTITUTION
        ).modifier
        character.hp += constitution_modifier
        character.max_hp = character.hp
        character.hp_increase = class_feature.hitpoints.hp_higher_levels
        proficiencies = Proficiencies.objects.get(class_feature=class_feature)
        proficiencies.character = character
        proficiencies.save()

    def form_valid(self, form):
        character = form.save(commit=False)
        character.user = self.request.user
        self._initialize_ability_scores(character, form)

        # Racial traits
        racial_trait = RacialTrait.objects.get(race=character.race)
        self._apply_racial_traits(character, racial_trait)
        self._apply_ability_score_increases(character, racial_trait)
        self._compute_ability_modifiers(character)

        # Class features
        self._apply_class_advancement(character, level=1)
        class_feature = ClassFeature.objects.get(class_name=character.class_name)
        self._apply_class_features(character, class_feature)

        character.save()

        # Inventory
        character.inventory = Inventory.objects.create()

        return super().form_valid(form)
