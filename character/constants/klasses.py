from django.db.models import TextChoices

from .abilities import AbilityName
from .equipment import ArmorType


class ClassName(TextChoices):
    """D&D 2024 SRD character class names."""

    BARBARIAN = "barbarian", "Barbarian"
    BARD = "bard", "Bard"
    CLERIC = "cleric", "Cleric"
    DRUID = "druid", "Druid"
    FIGHTER = "fighter", "Fighter"
    MONK = "monk", "Monk"
    PALADIN = "paladin", "Paladin"
    RANGER = "ranger", "Ranger"
    ROGUE = "rogue", "Rogue"
    SORCERER = "sorcerer", "Sorcerer"
    WARLOCK = "warlock", "Warlock"
    WIZARD = "wizard", "Wizard"


class WeaponCategory(TextChoices):
    """Weapon proficiency categories."""

    SIMPLE = "simple", "Simple Weapons"
    MARTIAL = "martial", "Martial Weapons"


# Legacy mapping for backwards compatibility during migration
KLASS_FEATURES: dict = {
    "C": {
        "hit_points": {
            "hit_dice": "1d8",
            "hp_first_level": 8,
            "hp_modifier_ability": AbilityName.CONSTITUTION,
            "hp_higher_levels": 5,
        },
        "proficiencies": {
            "armor": {
                ArmorType.LIGHT_ARMOR,
                ArmorType.MEDIUM_ARMOR,
                ArmorType.SHIELD,
            },
            "saving_throws": {AbilityName.WISDOM, AbilityName.CHARISMA},
        },
        "wealth": "5d4",
    },
    "F": {
        "hit_points": {
            "hit_dice": "1d10",
            "hp_first_level": 10,
            "hp_modifier_ability": AbilityName.CONSTITUTION,
            "hp_higher_levels": 6,
        },
        "proficiencies": {
            "armor": {
                ArmorType.LIGHT_ARMOR,
                ArmorType.MEDIUM_ARMOR,
                ArmorType.HEAVY_ARMOR,
                ArmorType.SHIELD,
            },
            "saving_throws": {AbilityName.STRENGTH, AbilityName.CONSTITUTION},
        },
        "wealth": "5d4",
    },
    "R": {
        "hit_points": {
            "hit_dice": "1d8",
            "hp_first_level": 8,
            "hp_modifier_ability": AbilityName.CONSTITUTION,
            "hp_higher_levels": 5,
        },
        "proficiencies": {
            "armor": {ArmorType.LIGHT_ARMOR},
            "saving_throws": {
                AbilityName.DEXTERITY,
                AbilityName.INTELLIGENCE,
            },
        },
        "wealth": "4d4",
    },
    "W": {
        "hit_points": {
            "hit_dice": "1d6",
            "hp_first_level": 6,
            "hp_modifier_ability": AbilityName.CONSTITUTION,
            "hp_higher_levels": 4,
        },
        "proficiencies": {
            "armor": set(),
            "saving_throws": {AbilityName.INTELLIGENCE, AbilityName.WISDOM},
        },
        "wealth": "4d4",
    },
}
