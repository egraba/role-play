from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, ListView

import character.abilities as abilities
import character.forms as cforms
import character.models as cmodels


class CharacterDetailView(LoginRequiredMixin, DetailView):
    model = cmodels.Character
    template_name = "character/character.html"


class CharacterListView(LoginRequiredMixin, ListView):
    model = cmodels.Character
    paginate_by = 20
    ordering = ["-xp"]
    template_name = "character/character_list.html"


class CharacterCreateView(LoginRequiredMixin, CreateView):
    model = cmodels.Character
    form_class = cforms.CreateCharacterForm
    template_name = "character/character_create.html"

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        character = form.save(commit=False)
        character.user = self.request.user

        # Apply racial traits
        racial_trait = cmodels.RacialTrait.objects.get(race=character.race)
        character.adult_age = racial_trait.adult_age
        character.life_expectancy = racial_trait.life_expectancy
        character.alignment = racial_trait.alignment
        character.size = racial_trait.size
        character.speed = racial_trait.speed
        character.save()
        character.languages.set(racial_trait.languages.all())
        character.abilities.set(racial_trait.abilities.all())

        # Apply ability score increases
        ability_score_increases = cmodels.AbilityScoreIncrease.objects.filter(
            racial_trait__race=racial_trait.race
        )
        for asi in ability_score_increases:
            if hasattr(character, asi.ability):
                old_value = getattr(character, asi.ability)
                new_value = old_value + asi.increase
                setattr(character, asi.ability, new_value)

        # Compute ability modifiers
        character.strength_modifier = abilities.compute_ability_modifier(
            character.strength
        )
        character.dexterity_modifier = abilities.compute_ability_modifier(
            character.dexterity
        )
        character.constitution_modifier = abilities.compute_ability_modifier(
            character.constitution
        )
        character.intelligence_modifier = abilities.compute_ability_modifier(
            character.intelligence
        )
        character.wisdom_modifier = abilities.compute_ability_modifier(character.wisdom)
        character.charisma_modifier = abilities.compute_ability_modifier(
            character.charisma
        )

        # Apply class advancement for Level 1
        class_advancement = cmodels.ClassAdvancement.objects.get(
            class_name=character.class_name, level=1
        )
        character.proficiency_bonus += class_advancement.proficiency_bonus

        character.save()
        return super().form_valid(form)
