from django.db.models import TextChoices

from ..constants.abilities import AbilityName


class Race(TextChoices):
    HUMAN = "human", "Human"
    HALFLING = "halfling", "Halfling"
    HILL_DWARF = "hill_dwarf", "Hill Dwarf"
    MOUNTAIN_DWARF = "mountain_dwarf", "Mountain Dwarf"
    HIGH_ELF = "high_elf", "High Elf"
    WOOD_ELF = "wood_elf", "Wood Elf"


class Alignment(TextChoices):
    LAWFUL = "L", "Lawful"
    FREEDOM = "F", "Freedom"
    NONE = "N", "None"


class Size(TextChoices):
    SMALL = "S", "Small"
    MEDIUM = "M", "Medium"


class LanguageName(TextChoices):
    COMMON = "C", "Common"
    DWARVISH = "D", "Dwarvish"
    ELVISH = "E", "Elvish"
    HALFLING = "H", "Halfling"


class SenseName(TextChoices):
    BRAVE = "BR", "Brave"
    DARKVISION = "DV", "Darkvision"
    DWARVEN_COMBAT_TRAINING = "DC", "Dwarven Combat Training"
    DWARVEN_RESILIENCE = "DR", "Dwarven Resilience"
    FEY_ANCESTRY = "FA", "Fey Ancestry"
    HALFLING_NIMBLENESS = "HN", "Halfling Nimbleness"
    KEEN_SENSES = "KS", "Keen Senses"
    LUCKY = "LU", "Lucky"
    STONECUNNING = "SC", "Stonecunning"
    TOOL_PROFICIENCY = "TP", "Tool Proficiency"
    TRANCE = "TR", "Trance"


RACIAL_TRAITS: dict = {
    Race.HILL_DWARF: {
        "adult_age": 50,
        "life_expectancy": 350,
        "alignment": Alignment.LAWFUL,
        "size": Size.MEDIUM,
        "speed": 25,
        "languages": {LanguageName.COMMON, LanguageName.DWARVISH},
        "senses": {
            SenseName.DARKVISION,
            SenseName.DWARVEN_RESILIENCE,
            SenseName.DWARVEN_COMBAT_TRAINING,
            SenseName.TOOL_PROFICIENCY,
            SenseName.STONECUNNING,
        },
        "ability_score_increases": {AbilityName.CONSTITUTION: 2},
    },
    Race.MOUNTAIN_DWARF: {
        "adult_age": 50,
        "life_expectancy": 350,
        "alignment": Alignment.LAWFUL,
        "size": Size.MEDIUM,
        "speed": 25,
        "languages": {LanguageName.COMMON, LanguageName.DWARVISH},
        "senses": {
            SenseName.DARKVISION,
            SenseName.DWARVEN_RESILIENCE,
            SenseName.DWARVEN_COMBAT_TRAINING,
            SenseName.TOOL_PROFICIENCY,
            SenseName.STONECUNNING,
        },
        "ability_score_increases": {AbilityName.CONSTITUTION: 2},
    },
    Race.HIGH_ELF: {
        "adult_age": 100,
        "life_expectancy": 750,
        "alignment": Alignment.FREEDOM,
        "size": Size.MEDIUM,
        "speed": 30,
        "languages": {LanguageName.COMMON, LanguageName.ELVISH},
        "senses": {
            SenseName.DARKVISION,
            SenseName.KEEN_SENSES,
            SenseName.FEY_ANCESTRY,
            SenseName.TRANCE,
        },
        "ability_score_increases": {AbilityName.DEXTERITY: 2},
    },
    Race.WOOD_ELF: {
        "adult_age": 100,
        "life_expectancy": 750,
        "alignment": Alignment.FREEDOM,
        "size": Size.MEDIUM,
        "speed": 30,
        "languages": {LanguageName.COMMON, LanguageName.ELVISH},
        "senses": {
            SenseName.DARKVISION,
            SenseName.KEEN_SENSES,
            SenseName.FEY_ANCESTRY,
            SenseName.TRANCE,
        },
        "ability_score_increases": {AbilityName.DEXTERITY: 2},
    },
    Race.HALFLING: {
        "adult_age": 20,
        "life_expectancy": 75,
        "alignment": Alignment.LAWFUL,
        "size": Size.SMALL,
        "speed": 25,
        "languages": {LanguageName.COMMON, LanguageName.HALFLING},
        "senses": {SenseName.LUCKY, SenseName.BRAVE, SenseName.HALFLING_NIMBLENESS},
        "ability_score_increases": {AbilityName.DEXTERITY: 2},
    },
    Race.HUMAN: {
        "adult_age": 50,
        "life_expectancy": 350,
        "alignment": Alignment.NONE,
        "size": Size.MEDIUM,
        "speed": 30,
        "languages": {LanguageName.COMMON},
        "senses": {},
        "ability_score_increases": {
            AbilityName.CHARISMA: 1,
            AbilityName.CONSTITUTION: 1,
            AbilityName.DEXTERITY: 1,
            AbilityName.INTELLIGENCE: 1,
            AbilityName.STRENGTH: 1,
            AbilityName.WISDOM: 1,
        },
    },
}
