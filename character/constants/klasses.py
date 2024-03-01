from ..models.abilities import AbilityType
from ..models.classes import Klass
from ..models.equipment import Armor

KLASS_FEATURES: dict = {
    Klass.CLERIC: {
        "hit_points": {
            "hit_dice": "1d8",
            "hp_first_level": 8,
            "hp_modifier_ability": AbilityType.Name.CONSTITUTION,
            "hp_higher_levels": 5,
        },
        "proficiencies": {
            "armor": {
                Armor.Type.LIGHT_ARMOR,
                Armor.Type.MEDIUM_ARMOR,
                Armor.Type.SHIELD,
            },
            "saving_throws": {AbilityType.Name.WISDOM, AbilityType.Name.CHARISMA},
        },
    },
    Klass.FIGHTER: {
        "hit_points": {
            "hit_dice": "1d10",
            "hp_first_level": 10,
            "hp_modifier_ability": AbilityType.Name.CONSTITUTION,
            "hp_higher_levels": 6,
        },
        "proficiencies": {
            "armor": {
                Armor.Type.LIGHT_ARMOR,
                Armor.Type.MEDIUM_ARMOR,
                Armor.Type.HEAVY_ARMOR,
                Armor.Type.SHIELD,
            },
            "saving_throws": {AbilityType.Name.STRENGTH, AbilityType.Name.CONSTITUTION},
        },
    },
    Klass.ROGUE: {
        "hit_points": {
            "hit_dice": "1d8",
            "hp_first_level": 8,
            "hp_modifier_ability": AbilityType.Name.CONSTITUTION,
            "hp_higher_levels": 5,
        },
        "proficiencies": {
            "armor": {Armor.Type.LIGHT_ARMOR},
            "saving_throws": {
                AbilityType.Name.DEXTERITY,
                AbilityType.Name.INTELLIGENCE,
            },
        },
    },
    Klass.WIZARD: {
        "hit_points": {
            "hit_dice": "1d6",
            "hp_first_level": 6,
            "hp_modifier_ability": AbilityType.Name.CONSTITUTION,
            "hp_higher_levels": 4,
        },
        "proficiencies": {
            "armor": {},
            "saving_throws": {AbilityType.Name.INTELLIGENCE, AbilityType.Name.WISDOM},
        },
    },
}
