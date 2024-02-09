from ..models.abilities import AbilityType
from ..models.classes import Class


def get_saving_throws(klass: Class) -> set[tuple[str, str]] | None:
    match klass:
        case Class.CLERIC:
            return {AbilityType.Name.WISDOM, AbilityType.Name.CHARISMA}
        case Class.FIGHTER:
            return {AbilityType.Name.STRENGTH, AbilityType.Name.CONSTITUTION}
        case Class.ROGUE:
            return {AbilityType.Name.DEXTERITY, AbilityType.Name.INTELLIGENCE}
        case Class.WIZARD:
            return {AbilityType.Name.INTELLIGENCE, AbilityType.Name.WISDOM}
        case _:
            return None
