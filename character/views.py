from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, ListView

import character.abilities as abilities
from character.forms import CreateCharacterForm
from character.models import (
    AbilityScoreIncrease,
    Character,
    ClassAdvancement,
    RacialTrait,
)


class CharacterDetailView(LoginRequiredMixin, DetailView):
    model = Character
    template_name = "character/character.html"


class CharacterListView(LoginRequiredMixin, ListView):
    model = Character
    paginate_by = 20
    ordering = ["-xp"]
    template_name = "character/character_list.html"


class CharacterCreateView(LoginRequiredMixin, CreateView):
    model = Character
    form_class = CreateCharacterForm
    template_name = "character/character_create.html"

    def get_success_url(self):
        return self.object.get_absolute_url()

    def _apply_racial_traits(self, character, racial_trait):
        character.adult_age = racial_trait.adult_age
        character.life_expectancy = racial_trait.life_expectancy
        character.alignment = racial_trait.alignment
        character.size = racial_trait.size
        character.speed = racial_trait.speed
        # Need to save before setting many-to-many relationships
        character.save()
        character.languages.set(racial_trait.languages.all())
        character.abilities.set(racial_trait.abilities.all())

    def _apply_ability_score_increases(self, character, racial_trait):
        ability_score_increases = cmodels.AbilityScoreIncrease.objects.filter(
            racial_trait__race=racial_trait.race
        )
        if ability_score_increases is not None:
            for asi in ability_score_increases:
                if hasattr(character, asi.ability):
                    old_value = getattr(character, asi.ability)
                    new_value = old_value + asi.increase
                    setattr(character, asi.ability, new_value)

    def _compute_ability_modifiers(self, character):
        character.strength_modifier = abilities.compute_modifier(character.strength)
        character.dexterity_modifier = abilities.compute_modifier(character.dexterity)
        character.constitution_modifier = abilities.compute_modifier(
            character.constitution
        )
        character.intelligence_modifier = abilities.compute_modifier(
            character.intelligence
        )
        character.wisdom_modifier = abilities.compute_modifier(character.wisdom)
        character.charisma_modifier = abilities.compute_modifier(character.charisma)

    def _apply_class_advancement(self, character, level):
        class_advancement = cmodels.ClassAdvancement.objects.get(
            class_name=character.class_name, level=1
        )
        character.proficiency_bonus += class_advancement.proficiency_bonus

    def _apply_class_features(self, character, class_feature):
        character.hit_dice = class_feature.hit_dice
        character.hp += class_feature.hp_first_level
        character.max_hp = character.hp

    def form_valid(self, form):
        character = form.save(commit=False)
        character.user = self.request.user

        # Racial traits
        racial_trait = cmodels.RacialTrait.objects.get(race=character.race)
        self._apply_racial_traits(character, racial_trait)
        self._apply_ability_score_increases(character, racial_trait)
        self._compute_ability_modifiers(character)

        # Class features
        self._apply_class_advancement(character, level=1)
        class_feature = cmodels.ClassFeature.objects.get(
            class_name=character.class_name
        )
        self._apply_class_features(character, class_feature)

        character.save()

        return super().form_valid(form)
