from ..constants.abilities import AbilityName
from ..models.klasses import Klass
from ..models.equipment import Armor

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
                Armor.Type.LIGHT_ARMOR,
                Armor.Type.MEDIUM_ARMOR,
                Armor.Type.SHIELD,
            },
            "saving_throws": {AbilityName.WISDOM, AbilityName.CHARISMA},
        },
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
                Armor.Type.LIGHT_ARMOR,
                Armor.Type.MEDIUM_ARMOR,
                Armor.Type.HEAVY_ARMOR,
                Armor.Type.SHIELD,
            },
            "saving_throws": {AbilityName.STRENGTH, AbilityName.CONSTITUTION},
        },
    },
    Klass.ROGUE: {
        "hit_points": {
            "hit_dice": "1d8",
            "hp_first_level": 8,
            "hp_modifier_ability": AbilityName.CONSTITUTION,
            "hp_higher_levels": 5,
        },
        "proficiencies": {
            "armor": {Armor.Type.LIGHT_ARMOR},
            "saving_throws": {
                AbilityName.DEXTERITY,
                AbilityName.INTELLIGENCE,
            },
        },
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
    },
}
