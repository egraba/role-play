import random
from abc import ABC, abstractmethod

from utils.dice import DiceString

from .constants.backgrounds import BACKGROUNDS
from .constants.klasses import KLASS_FEATURES
from .forms.character import CharacterCreateForm
from .models.abilities import Ability, AbilityType
from .models.character import Character
from .models.equipment import Inventory, ToolSettings
from .models.feats import CharacterFeat, Feat
from .models.proficiencies import (
    SavingThrowProficiency,
    SkillProficiency,
    ToolProficiency,
)
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


class SpeciesBuilder(CharacterAttributesBuilder):
    """Apply species traits to a character (D&D 2024 rules)."""

    def __init__(self, character: Character) -> None:
        self.character = character
        self.species = character.species

    def _apply_species_traits(self) -> None:
        """Apply size, speed, and languages from species."""
        if not self.species:
            return
        self.character.size = self.species.size
        self.character.speed = self.species.speed
        # Need to save before setting many-to-many relationships
        self.character.save()
        for language in self.species.languages.all():
            self.character.languages.add(language)

    def build(self) -> None:
        self._apply_species_traits()
        self.character.save()


class KlassBuilder(CharacterAttributesBuilder):
    def __init__(self, character: Character) -> None:
        self.character = character
        self.klass = character.klass

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

    def _add_tool_proficiency(self) -> None:
        """Grant tool proficiency from background."""
        tool_name = BACKGROUNDS[self.background].get("tool_proficiency")
        if tool_name:
            tool = ToolSettings.objects.get(name=tool_name)
            ToolProficiency.objects.create(character=self.character, tool=tool)

    def _add_origin_feat(self) -> None:
        """Grant origin feat from background."""
        feat_name = BACKGROUNDS[self.background].get("origin_feat")
        if feat_name:
            feat = Feat.objects.get(name=feat_name)
            CharacterFeat.objects.create(
                character=self.character, feat=feat, granted_by="background"
            )

    def _add_starting_gold(self) -> None:
        """Add 50 GP starting equipment (2024 rules)."""
        self.character.inventory.gp += 50
        self.character.inventory.save()

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
        self._add_tool_proficiency()
        self._add_origin_feat()
        self._add_starting_gold()
        self._select_personality_trait()
        self._select_ideal()
        self._select_bond()
        self._select_flaw()
        self.character.save()
