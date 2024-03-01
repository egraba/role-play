from utils.converters import duplicate_choice

from ..models.character import Skill
from ..models.classes import Klass


def get_skills(klass: Klass) -> set[tuple[str, str]] | None:
    match klass:
        case Klass.CLERIC:
            return {
                duplicate_choice(Skill.Name.HISTORY),
                duplicate_choice(Skill.Name.INSIGHT),
                duplicate_choice(Skill.Name.MEDICINE),
                duplicate_choice(Skill.Name.PERSUASION),
                duplicate_choice(Skill.Name.RELIGION),
            }
        case Klass.FIGHTER:
            return {
                duplicate_choice(Skill.Name.ACROBATICS),
                duplicate_choice(Skill.Name.ANIMAL_HANDLING),
                duplicate_choice(Skill.Name.ATHLETICS),
                duplicate_choice(Skill.Name.HISTORY),
                duplicate_choice(Skill.Name.INSIGHT),
                duplicate_choice(Skill.Name.INTIMIDATION),
                duplicate_choice(Skill.Name.PERCEPTION),
                duplicate_choice(Skill.Name.SURVIVAL),
            }
        case Klass.ROGUE:
            return {
                duplicate_choice(Skill.Name.ACROBATICS),
                duplicate_choice(Skill.Name.ATHLETICS),
                duplicate_choice(Skill.Name.DECEPTION),
                duplicate_choice(Skill.Name.INSIGHT),
                duplicate_choice(Skill.Name.INTIMIDATION),
                duplicate_choice(Skill.Name.INVESTIGATION),
                duplicate_choice(Skill.Name.PERCEPTION),
                duplicate_choice(Skill.Name.PERFORMANCE),
                duplicate_choice(Skill.Name.PERSUASION),
                duplicate_choice(Skill.Name.SLEIGHT_OF_HAND),
                duplicate_choice(Skill.Name.STEALTH),
            }
        case Klass.WIZARD:
            return {
                duplicate_choice(Skill.Name.ARCANA),
                duplicate_choice(Skill.Name.HISTORY),
                duplicate_choice(Skill.Name.INSIGHT),
                duplicate_choice(Skill.Name.INVESTIGATION),
                duplicate_choice(Skill.Name.MEDICINE),
                duplicate_choice(Skill.Name.RELIGION),
            }
        case _:
            return None
