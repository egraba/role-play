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
    COMMON = "common", "Common"
    DWARVISH = "dwarvish", "Dwarvish"
    ELVISH = "elvish", "Elvish"
    GIANT = "giant", "Giant"
    GNOMISH = "gnomish", "Gnomish"
    GOBLIN = "goblin", "Goblin"
    HALFLING = "halfling", "Halfling"
    ORC = "orc", "Orc"
    ABYSSAL = "abyssal", "Abyssal"
    CELESTIAL = "celestial", "Celestial"
    DEEP_SPEECH = "deep_speech", "Deep Speech"
    DRACONIC = "draconic", "Draconic"
    INFERNAL = "infernal", "Infernal"
    PRIMORDIAL = "primordial", "Primordial"
    SYLVAN = "sylvan", "Sylvan"
    UNDERCOMMON = "undercommon", "Undercommon"


class LanguageType(TextChoices):
    STANDARD = "S", "Standard"
    EXOTIC = "E", "Exotic"


class SenseName(TextChoices):
    BRAVE = "brave", "Brave"
    CANTRIP = "cantrip", "Cantrip"
    DARKVISION = "darkvision", "Darkvision"
    DWARVEN_ARMOR_TRAINING = "dwarven_armor_training", "Dwarven Armor Training"
    DWARVEN_COMBAT_TRAINING = "dwarven_combat_training", "Dwarven Combat Training"
    DWARVEN_RESILIENCE = "dwarven_resilience", "Dwarven Resilience"
    DWARVEN_TOUGHNESS = "dwarven_toughness", "Dwarven Toughness"
    ELF_WEAPON_TRAINING = "elf_weapon_training", "Elf Weapon Training"
    EXTRA_LANGUAGE = "extra_language", "Extra Language"
    FEY_ANCESTRY = "fey_ancestry", "Fey Ancestry"
    FLEET_OF_FOOT = "fleet_of_foot", "Fleet of Foot"
    HALFLING_NIMBLENESS = "halfling_nimbleness", "Halfling Nimbleness"
    KEEN_SENSES = "keen_senses", "Keen Senses"
    LUCKY = "lucky", "Lucky"
    MASK_OF_THE_WILD = "mask_of_the_wild", "Mask of the Wild"
    STONECUNNING = "stonecunning", "Stonecunning"
    TOOL_PROFICIENCY = "tool_proficiency", "Tool Proficiency"
    TRANCE = "trance", "Trance"


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
            SenseName.DWARVEN_TOUGHNESS,
        },
        "ability_score_increases": {AbilityName.CONSTITUTION: 2, AbilityName.WISDOM: 1},
        "height": {
            "base_height": 3.8,
            "height_modifier": "2d4",
        },
        "weight": {
            "base_weight": 115,
            "weight_modifier": "2d6",
        },
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
            SenseName.DWARVEN_ARMOR_TRAINING,
        },
        "ability_score_increases": {
            AbilityName.CONSTITUTION: 2,
            AbilityName.STRENGTH: 2,
        },
        "height": {
            "base_height": 4.0,
            "height_modifier": "2d4",
        },
        "weight": {
            "base_weight": 130,
            "weight_modifier": "2d6",
        },
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
            SenseName.ELF_WEAPON_TRAINING,
            SenseName.CANTRIP,
            SenseName.EXTRA_LANGUAGE,
        },
        "ability_score_increases": {
            AbilityName.DEXTERITY: 2,
            AbilityName.INTELLIGENCE: 1,
        },
        "height": {
            "base_height": 4.6,
            "height_modifier": "2d10",
        },
        "weight": {
            "base_weight": 90,
            "weight_modifier": "1d4",
        },
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
            SenseName.ELF_WEAPON_TRAINING,
            SenseName.FLEET_OF_FOOT,
            SenseName.MASK_OF_THE_WILD,
        },
        "ability_score_increases": {AbilityName.DEXTERITY: 2, AbilityName.WISDOM: 1},
        "height": {
            "base_height": 4.6,
            "height_modifier": "2d10",
        },
        "weight": {
            "base_weight": 100,
            "weight_modifier": "1d4",
        },
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
        "height": {
            "base_height": 2.7,
            "height_modifier": "2d4",
        },
        "weight": {
            "base_weight": 35,
            "weight_modifier": None,
        },
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
        "height": {
            "base_height": 4.8,
            "height_modifier": "2d10",
        },
        "weight": {
            "base_weight": 110,
            "weight_modifier": "2d4",
        },
    },
}
