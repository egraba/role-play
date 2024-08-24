from ..constants.abilities import AbilityName
from ..constants.equipment import ArmorType
from ..models.klasses import Klass

KLASS_FEATURES: dict = {
    Klass.CLERIC: {
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
    Klass.FIGHTER: {
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
    Klass.ROGUE: {
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
    Klass.WIZARD: {
        "hit_points": {
            "hit_dice": "1d6",
            "hp_first_level": 6,
            "hp_modifier_ability": AbilityName.CONSTITUTION,
            "hp_higher_levels": 4,
        },
        "proficiencies": {
            "armor": {},
            "saving_throws": {AbilityName.INTELLIGENCE, AbilityName.WISDOM},
        },
        "wealth": "4d4",
    },
}
