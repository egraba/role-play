from abc import ABC, abstractmethod

from utils.dice import Dice
from ..models.abilities import AbilityType
from ..models.character import Character
from ..models.races import Alignment, Language, Sense, Size
from ..models.classes import ClassAdvancement
from ..models.proficiencies import SavingThrowProficiency
from .abilities import compute_ability_modifier
from .proficiencies import saving_throws
from ..constants.klasses import hit_points


class RaceBuilder(ABC):
    def __init__(self, character: Character) -> None:
        self.character = character

    @abstractmethod
    def apply_racial_traits(self) -> None:
        pass

    @abstractmethod
    def apply_ability_score_increases(self) -> None:
        pass

    def compute_ability_modifiers(self) -> None:
        for ability in self.character.abilities.all():
            ability.modifier = compute_ability_modifier(ability.score)


class DwarfBuilder(RaceBuilder):
    def apply_racial_traits(self):
        self.character.adult_age = 50
        self.character.life_expectancy = 350
        self.character.alignment = Alignment.LAWFUL
        self.character.size = Size.MEDIUM
        self.character.speed = 25
        # Need to save before setting many-to-many relationships
        self.character.save()
        self.character.languages.add(Language.objects.get(name=Language.Name.COMMON))
        self.character.languages.add(Language.objects.get(name=Language.Name.DWARVISH))
        self.character.senses.add(Sense.objects.get(name=Sense.Name.DARKVISION))
        self.character.senses.add(Sense.objects.get(name=Sense.Name.DWARVEN_RESILIENCE))
        self.character.senses.add(
            Sense.objects.get(name=Sense.Name.DWARVEN_COMBAT_TRAINING)
        )
        self.character.senses.add(Sense.objects.get(name=Sense.Name.TOOL_PROFICIENCY))
        self.character.senses.add(Sense.objects.get(name=Sense.Name.STONECUNNING))

    def apply_ability_score_increases(self):
        ability = self.character.abilities.get(
            ability_type=AbilityType.Name.CONSTITUTION
        )
        ability.score += 2
        ability.save()


class ElfBuilder(RaceBuilder):
    def apply_racial_traits(self):
        self.character.adult_age = 100
        self.character.life_expectancy = 750
        self.character.alignment = Alignment.FREEDOM
        self.character.size = Size.MEDIUM
        self.character.speed = 30
        # Need to save before setting many-to-many relationships
        self.character.save()
        self.character.languages.add(Language.objects.get(name=Language.Name.COMMON))
        self.character.languages.add(Language.objects.get(name=Language.Name.ELVISH))
        self.character.senses.add(Sense.objects.get(name=Sense.Name.DARKVISION))
        self.character.senses.add(Sense.objects.get(name=Sense.Name.KEEN_SENSES))
        self.character.senses.add(Sense.objects.get(name=Sense.Name.FEY_ANCESTRY))
        self.character.senses.add(Sense.objects.get(name=Sense.Name.TRANCE))

    def apply_ability_score_increases(self):
        ability = self.character.abilities.get(ability_type=AbilityType.Name.DEXTERITY)
        ability.score += 2
        ability.save()


class HalflingBuilder(RaceBuilder):
    def apply_racial_traits(self):
        self.character.adult_age = 20
        self.character.life_expectancy = 75
        self.character.alignment = Alignment.LAWFUL
        self.character.size = Size.SMALL
        self.character.speed = 25
        # Need to save before setting many-to-many relationships
        self.character.save()
        self.character.languages.add(Language.objects.get(name=Language.Name.COMMON))
        self.character.languages.add(Language.objects.get(name=Language.Name.HALFLING))
        self.character.senses.add(Sense.objects.get(name=Sense.Name.LUCKY))
        self.character.senses.add(Sense.objects.get(name=Sense.Name.BRAVE))
        self.character.senses.add(
            Sense.objects.get(name=Sense.Name.HALFLING_NIMBLENESS)
        )

    def apply_ability_score_increases(self):
        ability = self.character.abilities.get(ability_type=AbilityType.Name.DEXTERITY)
        ability.score += 2
        ability.save()


class HumanBuilder(RaceBuilder):
    def apply_racial_traits(self):
        self.character.adult_age = 20
        self.character.life_expectancy = 90
        self.character.alignment = Alignment.NONE
        self.character.size = Size.MEDIUM
        self.character.speed = 30
        # Need to save before setting many-to-many relationships
        self.character.save()
        self.character.languages.add(Language.objects.get(name=Language.Name.COMMON))

    def apply_ability_score_increases(self):
        for ability in self.character.abilities.all():
            ability.score += 1
            ability.save()


class KlassBuilder:
    def __init__(self, character: Character) -> None:
        self.character = character
        self.klass = character.class_name

    def apply_advancement(self) -> None:
        class_advancement = ClassAdvancement.objects.get(
            class_name=self.character.class_name, level=1
        )
        self.character.proficiency_bonus += class_advancement.proficiency_bonus

    def apply_hit_points(self) -> None:
        self.character.hit_dice = Dice(hit_points[self.klass]["hit_dice"])
        self.character.hp += hit_points[self.klass]["hp_first_level"]
        modifier = self.character.abilities.get(
            ability_type=hit_points[self.klass]["hp_modifier_ability"]
        ).modifier
        self.character.hp += modifier
        self.character.max_hp = self.character.hp
        self.character.hp_increase = hit_points[self.klass]["hp_higher_levels"]

    def apply_armor_proficiencies(self) -> None:
        pass

    def apply_weapons_proficiencies(self) -> None:
        pass

    def apply_tools_proficiencies(self) -> None:
        pass

    def apply_saving_throws_proficiencies(self) -> None:
        for ability in saving_throws[self.character.class_name]:
            SavingThrowProficiency.objects.create(
                character=self.character,
                ability_type=AbilityType.objects.get(name=ability),
            )


class Director:
    def build(self, race_builder: RaceBuilder, klass_builder: KlassBuilder) -> None:
        race_builder.apply_racial_traits()
        race_builder.apply_ability_score_increases()
        race_builder.compute_ability_modifiers()
        klass_builder.apply_advancement()
        klass_builder.apply_hit_points()
        klass_builder.apply_armor_proficiencies()
        klass_builder.apply_weapons_proficiencies()
        klass_builder.apply_tools_proficiencies()
        klass_builder.apply_saving_throws_proficiencies()
