from ..constants.abilities import AbilityName
from ..models.races import Alignment, Language, Race, Sense, Size

RACIAL_TRAITS: dict = {
    Race.DWARF: {
        "adult_age": 50,
        "life_expectancy": 350,
        "alignment": Alignment.LAWFUL,
        "size": Size.MEDIUM,
        "speed": 25,
        "languages": {Language.Name.COMMON, Language.Name.DWARVISH},
        "senses": {
            Sense.Name.DARKVISION,
            Sense.Name.DWARVEN_RESILIENCE,
            Sense.Name.DWARVEN_COMBAT_TRAINING,
            Sense.Name.TOOL_PROFICIENCY,
            Sense.Name.STONECUNNING,
        },
        "ability_score_increases": {AbilityName.CONSTITUTION: 2},
    },
    Race.ELF: {
        "adult_age": 100,
        "life_expectancy": 750,
        "alignment": Alignment.FREEDOM,
        "size": Size.MEDIUM,
        "speed": 30,
        "languages": {Language.Name.COMMON, Language.Name.ELVISH},
        "senses": {
            Sense.Name.DARKVISION,
            Sense.Name.KEEN_SENSES,
            Sense.Name.FEY_ANCESTRY,
            Sense.Name.TRANCE,
        },
        "ability_score_increases": {AbilityName.DEXTERITY: 2},
    },
    Race.HALFLING: {
        "adult_age": 20,
        "life_expectancy": 75,
        "alignment": Alignment.LAWFUL,
        "size": Size.SMALL,
        "speed": 25,
        "languages": {Language.Name.COMMON, Language.Name.HALFLING},
        "senses": {Sense.Name.LUCKY, Sense.Name.BRAVE, Sense.Name.HALFLING_NIMBLENESS},
        "ability_score_increases": {AbilityName.DEXTERITY: 2},
    },
    Race.HUMAN: {
        "adult_age": 50,
        "life_expectancy": 350,
        "alignment": Alignment.NONE,
        "size": Size.MEDIUM,
        "speed": 30,
        "languages": {Language.Name.COMMON},
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
