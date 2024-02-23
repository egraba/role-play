from abc import ABC, abstractmethod

from ..models.abilities import AbilityType
from ..models.character import Character
from ..models.races import Alignment, Language, Sense, Size
from .abilities import compute_ability_modifier


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
    def apply_racial_traits(self) -> None:
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

    def apply_ability_score_increases(self) -> None:
        ability = self.character.abilities.get(
            ability_type=AbilityType.Name.CONSTITUTION
        )
        ability.score += 2
        ability.save()


class RaceDirector:
    def build(self, builder: RaceBuilder):
        builder.apply_racial_traits()
        builder.apply_ability_score_increases()
        builder.compute_ability_modifiers()
