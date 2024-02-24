from ..models.abilities import AbilityType
from ..models.classes import Class

klass_features: dict = {
    Class.CLERIC: {
        "hit_points": {
            "hit_dice": "1d8",
            "hp_first_level": 8,
            "hp_modifier_ability": AbilityType.Name.CONSTITUTION,
            "hp_higher_levels": 5,
        },
        "saving_throws": {AbilityType.Name.WISDOM, AbilityType.Name.CHARISMA},
    },
    Class.FIGHTER: {
        "hit_points": {
            "hit_dice": "1d10",
            "hp_first_level": 10,
            "hp_modifier_ability": AbilityType.Name.CONSTITUTION,
            "hp_higher_levels": 6,
        },
        "saving_throws": {AbilityType.Name.STRENGTH, AbilityType.Name.CONSTITUTION},
    },
    Class.ROGUE: {
        "hit_points": {
            "hit_dice": "1d8",
            "hp_first_level": 8,
            "hp_modifier_ability": AbilityType.Name.CONSTITUTION,
            "hp_higher_levels": 5,
        },
        "saving_throws": {AbilityType.Name.DEXTERITY, AbilityType.Name.INTELLIGENCE},
    },
    Class.WIZARD: {
        "hit_points": {
            "hit_dice": "1d6",
            "hp_first_level": 6,
            "hp_modifier_ability": AbilityType.Name.CONSTITUTION,
            "hp_higher_levels": 4,
        },
        "saving_throws": {AbilityType.Name.INTELLIGENCE, AbilityType.Name.WISDOM},
    },
}
