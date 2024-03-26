import random

from utils.dice import Dice

from ..constants.backgrounds import BACKGROUNDS
from ..constants.klasses import KLASS_FEATURES
from ..constants.races import RACIAL_TRAITS
from ..forms.character import CharacterCreateForm
from ..models.abilities import Ability, AbilityType
from ..models.character import Character
from ..models.klasses import KlassAdvancement
from ..models.proficiencies import SavingThrowProficiency, SkillProficiency
from ..models.races import Language, Sense
from ..models.skills import Skill
from .abilities import compute_ability_modifier


class _BaseBuilder:
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


class _RaceBuilder:
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

    def set_height(self) -> None:
        base_height = RACIAL_TRAITS[self.race]["height"]["base_height"]
        height_modifier = RACIAL_TRAITS[self.race]["height"]["height_modifier"]
        additional_height = Dice(height_modifier).roll() / 12  # inches
        self.character.height = base_height + additional_height

    def set_weight(self) -> None:
        base_weight = RACIAL_TRAITS[self.race]["weight"]["base_weight"]
        weight_modifier = RACIAL_TRAITS[self.race]["weight"]["weight_modifier"]
        if weight_modifier is None:
            self.character.weight = base_weight
        else:
            additional_weight = Dice(weight_modifier).roll() * 12  # pounds
            self.character.weight = base_weight + additional_weight


class _KlassBuilder:
    def __init__(self, character: Character) -> None:
        self.character = character
        self.klass = character.klass

    def apply_advancement(self) -> None:
        klass_advancement = KlassAdvancement.objects.get(
            klass=self.character.klass, level=1
        )
        self.character.proficiency_bonus += klass_advancement.proficiency_bonus

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

    def add_wealth(self) -> None:
        wealth_roll = Dice(KLASS_FEATURES[self.klass]["wealth"]).roll()
        inventory = self.character.inventory
        inventory.gp = wealth_roll * 10
        inventory.save()


class _BackgroundBuilder:
    def __init__(self, character: Character) -> None:
        self.character = character
        self.background = character.background

    def add_skill_proficiencies(self) -> None:
        skill_proficiencies = BACKGROUNDS[self.background]["skill_proficiencies"]
        for skill in skill_proficiencies:
            SkillProficiency.objects.create(
                character=self.character, skill=Skill.objects.get(name=skill)
            )

    def add_tool_proficiencies(self) -> None:
        pass

    def add_languages(self) -> None:
        pass

    def add_equipment(self) -> None:
        pass

    def select_personality_trait(self) -> None:
        self.character.personality_trait = random.choice(
            list(BACKGROUNDS[self.background]["personality_traits"].values())
        )

    def select_ideal(self) -> None:
        self.character.ideal = random.choice(
            list(BACKGROUNDS[self.background]["ideals"].values())
        )

    def select_bond(self) -> None:
        self.character.bond = random.choice(
            list(BACKGROUNDS[self.background]["bonds"].values())
        )

    def select_flaw(self) -> None:
        self.character.flaw = random.choice(
            list(BACKGROUNDS[self.background]["flaws"].values())
        )


def build_character(character: Character, form: CharacterCreateForm) -> None:
    """
    Build character depending on its attributes (race, class, background, etc.).
    """
    base_builder = _BaseBuilder(character, form)
    race_builder = _RaceBuilder(character)
    klass_builder = _KlassBuilder(character)
    background_builder = _BackgroundBuilder(character)

    base_builder.initialize_ability_scores()

    race_builder.apply_racial_traits()
    race_builder.apply_ability_score_increases()
    race_builder.compute_ability_modifiers()
    race_builder.set_height()
    race_builder.set_weight()

    klass_builder.apply_advancement()
    klass_builder.apply_hit_points()
    klass_builder.apply_armor_proficiencies()
    klass_builder.apply_weapons_proficiencies()
    klass_builder.apply_tools_proficiencies()
    klass_builder.apply_saving_throws_proficiencies()
    klass_builder.add_wealth()

    background_builder.add_skill_proficiencies()
    background_builder.add_tool_proficiencies()
    background_builder.add_languages()
    background_builder.add_equipment()
    background_builder.select_personality_trait()
    background_builder.select_ideal()
    background_builder.select_bond()
    background_builder.select_flaw()
