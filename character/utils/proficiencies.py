from utils.converters import duplicate_choice

from ..constants.skills import SkillName
from ..models.klasses import Klass


def get_skills(klass: Klass) -> set[tuple[str, str]] | None:
    match klass:
        case Klass.CLERIC:
            return {
                duplicate_choice(SkillName.HISTORY),
                duplicate_choice(SkillName.INSIGHT),
                duplicate_choice(SkillName.MEDICINE),
                duplicate_choice(SkillName.PERSUASION),
                duplicate_choice(SkillName.RELIGION),
            }
        case Klass.FIGHTER:
            return {
                duplicate_choice(SkillName.ACROBATICS),
                duplicate_choice(SkillName.ANIMAL_HANDLING),
                duplicate_choice(SkillName.ATHLETICS),
                duplicate_choice(SkillName.HISTORY),
                duplicate_choice(SkillName.INSIGHT),
                duplicate_choice(SkillName.INTIMIDATION),
                duplicate_choice(SkillName.PERCEPTION),
                duplicate_choice(SkillName.SURVIVAL),
            }
        case Klass.ROGUE:
            return {
                duplicate_choice(SkillName.ACROBATICS),
                duplicate_choice(SkillName.ATHLETICS),
                duplicate_choice(SkillName.DECEPTION),
                duplicate_choice(SkillName.INSIGHT),
                duplicate_choice(SkillName.INTIMIDATION),
                duplicate_choice(SkillName.INVESTIGATION),
                duplicate_choice(SkillName.PERCEPTION),
                duplicate_choice(SkillName.PERFORMANCE),
                duplicate_choice(SkillName.PERSUASION),
                duplicate_choice(SkillName.SLEIGHT_OF_HAND),
                duplicate_choice(SkillName.STEALTH),
            }
        case Klass.WIZARD:
            return {
                duplicate_choice(SkillName.ARCANA),
                duplicate_choice(SkillName.HISTORY),
                duplicate_choice(SkillName.INSIGHT),
                duplicate_choice(SkillName.INVESTIGATION),
                duplicate_choice(SkillName.MEDICINE),
                duplicate_choice(SkillName.RELIGION),
            }
        case _:
            return None
