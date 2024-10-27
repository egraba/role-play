import random
from abc import ABC, abstractmethod

from utils.dice import DiceString

from .ability_modifiers import compute_ability_modifier
from .constants.backgrounds import BACKGROUNDS
from .constants.klasses import KLASS_FEATURES
from .constants.races import RACIAL_TRAITS
from .forms.character import CharacterCreateForm
from .models.abilities import Ability, AbilityType
from .models.character import Character
from .models.equipment import Inventory
from .models.klasses import KlassAdvancement
from .models.proficiencies import SavingThrowProficiency, SkillProficiency
from .models.races import Language, Sense
from .models.skills import Skill


class CharacterAttributesBuilder(ABC):
    @abstractmethod
    def build(self) -> None:
        pass


class BaseBuilder(CharacterAttributesBuilder):
    def __init__(self, character: Character, form: CharacterCreateForm) -> None:
        self.character = character
        self.form = form

    def _add_inventory(self) -> None:
        self.character.inventory = Inventory.objects.create()

    def _initialize_ability_scores(self) -> None:
        for ability_type in AbilityType.objects.all():
            ability = Ability.objects.create(
                ability_type=ability_type,
                score=self.form.cleaned_data[ability_type.get_name_display().lower()],
            )
            self.character.abilities.add(ability)

    def build(self) -> None:
        self._add_inventory()
        self.character.save()
        self._initialize_ability_scores()


class RaceBuilder(CharacterAttributesBuilder):
    def __init__(self, character: Character) -> None:
        self.character = character
        self.race = character.race

    def _apply_racial_traits(self) -> None:
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

    def _apply_ability_score_increases(self) -> None:
        increases = RACIAL_TRAITS[self.race]["ability_score_increases"]
        for increase in increases:
            ability = self.character.abilities.get(ability_type__name=increase)
            ability.score += increases[increase]
            ability.save()

    def _compute_ability_modifiers(self) -> None:
        for ability in self.character.abilities.all():
            ability.modifier = compute_ability_modifier(ability.score)

    def _set_height(self) -> None:
        base_height = RACIAL_TRAITS[self.race]["height"]["base_height"]
        height_modifier = RACIAL_TRAITS[self.race]["height"]["height_modifier"]
        additional_height = DiceString(height_modifier).roll() / 12  # inches
        self.character.height = base_height + additional_height

    def _set_weight(self) -> None:
        base_weight = RACIAL_TRAITS[self.race]["weight"]["base_weight"]
        weight_modifier = RACIAL_TRAITS[self.race]["weight"]["weight_modifier"]
        if weight_modifier is None:
            self.character.weight = base_weight
        else:
            additional_weight = DiceString(weight_modifier).roll() * 12  # pounds
            self.character.weight = base_weight + additional_weight

    def build(self) -> None:
        self._apply_racial_traits()
        self._apply_ability_score_increases()
        self._compute_ability_modifiers()
        self._set_height()
        self._set_weight()
        self.character.save()


class KlassBuilder(CharacterAttributesBuilder):
    def __init__(self, character: Character) -> None:
        self.character = character
        self.klass = character.klass

    def _apply_advancement(self) -> None:
        klass_advancement = KlassAdvancement.objects.get(
            klass=self.character.klass, level=1
        )
        self.character.proficiency_bonus += klass_advancement.proficiency_bonus

    def _apply_hit_points(self) -> None:
        hit_points = KLASS_FEATURES[self.klass]["hit_points"]
        self.character.hit_dice = DiceString(hit_points["hit_dice"])
        self.character.hp += hit_points["hp_first_level"]
        modifier = self.character.abilities.get(
            ability_type=hit_points["hp_modifier_ability"]
        ).modifier
        self.character.hp += modifier
        self.character.max_hp = self.character.hp
        self.character.hp_increase = hit_points["hp_higher_levels"]

    def _apply_armor_proficiencies(self) -> None:
        pass

    def _apply_weapons_proficiencies(self) -> None:
        pass

    def _apply_tools_proficiencies(self) -> None:
        pass

    def _apply_saving_throws_proficiencies(self) -> None:
        saving_throws = KLASS_FEATURES[self.klass]["proficiencies"]["saving_throws"]
        for ability in saving_throws:
            SavingThrowProficiency.objects.create(
                character=self.character,
                ability_type=AbilityType.objects.get(name=ability),
            )

    def _add_wealth(self) -> None:
        wealth_roll = DiceString(KLASS_FEATURES[self.klass]["wealth"]).roll()
        inventory = self.character.inventory
        inventory.gp = wealth_roll * 10
        inventory.save()

    def build(self) -> None:
        self._apply_advancement()
        self._apply_hit_points()
        self._apply_armor_proficiencies()
        self._apply_weapons_proficiencies()
        self._apply_tools_proficiencies()
        self._apply_saving_throws_proficiencies()
        self._add_wealth()
        self.character.save()


class BackgroundBuilder:
    def __init__(self, character: Character) -> None:
        self.character = character
        self.background = character.background

    def _add_skill_proficiencies(self) -> None:
        skill_proficiencies = BACKGROUNDS[self.background]["skill_proficiencies"]
        for skill in skill_proficiencies:
            SkillProficiency.objects.create(
                character=self.character, skill=Skill.objects.get(name=skill)
            )

    def _add_tool_proficiencies(self) -> None:
        pass

    def _add_languages(self) -> None:
        pass

    def _add_equipment(self) -> None:
        pass

    def _select_personality_trait(self) -> None:
        self.character.personality_trait = random.choice(
            list(BACKGROUNDS[self.background]["personality_traits"].values())
        )

    def _select_ideal(self) -> None:
        self.character.ideal = random.choice(
            list(BACKGROUNDS[self.background]["ideals"].values())
        )

    def _select_bond(self) -> None:
        self.character.bond = random.choice(
            list(BACKGROUNDS[self.background]["bonds"].values())
        )

    def _select_flaw(self) -> None:
        self.character.flaw = random.choice(
            list(BACKGROUNDS[self.background]["flaws"].values())
        )

    def build(self) -> None:
        self._add_skill_proficiencies()
        self._add_tool_proficiencies()
        self._add_languages()
        self._add_equipment()
        self._select_personality_trait()
        self._select_ideal()
        self._select_bond()
        self._select_flaw()
