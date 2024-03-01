from utils.dice import Dice

from ..constants.klasses import KLASS_FEATURES
from ..constants.races import RACIAL_TRAITS
from ..forms.character import CharacterCreateForm
from ..models.abilities import AbilityType, Ability
from ..models.character import Character
from ..models.klasses import KlassAdvancement
from ..models.proficiencies import SavingThrowProficiency
from ..models.races import Language, Sense
from .abilities import compute_ability_modifier


class BaseBuilder:
    def __init__(self, character: Character, form: CharacterCreateForm) -> None:
        self.character = character
        self.form = form

    def initialize_ability_scores(self) -> None:
        for ability_type in AbilityType.objects.all():
            ability = Ability.objects.create(
                ability_type=ability_type,
                score=self.form.cleaned_data[ability_type.get_name_display().lower()],
            )
            self.character.save()
            self.character.abilities.add(ability)


class RaceBuilder:
    def __init__(self, character: Character) -> None:
        self.character = character
        self.race = character.race

    def apply_racial_traits(self) -> None:
        self.character.adult_age = RACIAL_TRAITS[self.race]["adult_age"]
        self.character.life_expectancy = RACIAL_TRAITS[self.race]["life_expectancy"]
        self.character.alignment = RACIAL_TRAITS[self.race]["alignment"]
        self.character.size = RACIAL_TRAITS[self.race]["size"]
        self.character.speed = RACIAL_TRAITS[self.race]["speed"]
        # Need to save before setting many-to-many relationships
        self.character.save()
        for language in RACIAL_TRAITS[self.race]["languages"]:
            self.character.languages.add(Language.objects.get(name=language))
        for sense in RACIAL_TRAITS[self.race]["senses"]:
            self.character.senses.add(Sense.objects.get(name=sense))

    def apply_ability_score_increases(self) -> None:
        increases = RACIAL_TRAITS[self.race]["ability_score_increases"]
        for increase in increases:
            ability = self.character.abilities.get(ability_type__name=increase)
            ability.score += increases[increase]
            ability.save()

    def compute_ability_modifiers(self) -> None:
        for ability in self.character.abilities.all():
            ability.modifier = compute_ability_modifier(ability.score)


class KlassBuilder:
    def __init__(self, character: Character) -> None:
        self.character = character
        self.klass = character.class_name

    def apply_advancement(self) -> None:
        class_advancement = KlassAdvancement.objects.get(
            class_name=self.character.class_name, level=1
        )
        self.character.proficiency_bonus += class_advancement.proficiency_bonus

    def apply_hit_points(self) -> None:
        hit_points = KLASS_FEATURES[self.klass]["hit_points"]
        self.character.hit_dice = Dice(hit_points["hit_dice"])
        self.character.hp += hit_points["hp_first_level"]
        modifier = self.character.abilities.get(
            ability_type=hit_points["hp_modifier_ability"]
        ).modifier
        self.character.hp += modifier
        self.character.max_hp = self.character.hp
        self.character.hp_increase = hit_points["hp_higher_levels"]

    def apply_armor_proficiencies(self) -> None:
        pass

    def apply_weapons_proficiencies(self) -> None:
        pass

    def apply_tools_proficiencies(self) -> None:
        pass

    def apply_saving_throws_proficiencies(self) -> None:
        saving_throws = KLASS_FEATURES[self.klass]["proficiencies"]["saving_throws"]
        for ability in saving_throws:
            SavingThrowProficiency.objects.create(
                character=self.character,
                ability_type=AbilityType.objects.get(name=ability),
            )


class Director:
    def build(
        self,
        base_builder: BaseBuilder,
        race_builder: RaceBuilder,
        klass_builder: KlassBuilder,
    ) -> None:
        base_builder.initialize_ability_scores()
        race_builder.apply_racial_traits()
        race_builder.apply_ability_score_increases()
        race_builder.compute_ability_modifiers()
        klass_builder.apply_advancement()
        klass_builder.apply_hit_points()
        klass_builder.apply_armor_proficiencies()
        klass_builder.apply_weapons_proficiencies()
        klass_builder.apply_tools_proficiencies()
        klass_builder.apply_saving_throws_proficiencies()
