from ..models.abilities import AbilityType
from ..models.classes import Class

hit_points: dict = {
    Class.CLERIC: {
        "hit_dice": "1d8",
        "hp_first_level": 8,
        "hp_modifier_ability": AbilityType.Name.CONSTITUTION,
        "hp_higher_levels": 5,
    },
    Class.FIGHTER: {
        "hit_dice": "1d10",
        "hp_first_level": 10,
        "hp_modifier_ability": AbilityType.Name.CONSTITUTION,
        "hp_higher_levels": 6,
    },
    Class.ROGUE: {
        "hit_dice": "1d8",
        "hp_first_level": 8,
        "hp_modifier_ability": AbilityType.Name.CONSTITUTION,
        "hp_higher_levels": 5,
    },
    Class.WIZARD: {
        "hit_dice": "1d6",
        "hp_first_level": 6,
        "hp_modifier_ability": AbilityType.Name.CONSTITUTION,
        "hp_higher_levels": 4,
    },
}
