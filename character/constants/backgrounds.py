from django.db.models import TextChoices
from .skills import SkillName


class Background(TextChoices):
    ACOLYTE = "acolyte", "Acolyte"
    CRIMINAL = "criminal", "Criminal"
    FOLK_HERO = "folk_hero", "Folk Hero"
    NOBLE = "noble", "Noble"
    SAGE = "sage", "Sage"
    SOLDIER = "soldier", "Soldier"


BACKGROUNDS: dict = {
    Background.ACOLYTE: {
        "skill_proficiencies": {SkillName.INSIGHT, SkillName.RELIGION},
        "tool_proficiencies": {},
        "languages": {},
        "equipment": {},
    },
    Background.CRIMINAL: {
        "skill_proficiencies": {SkillName.DECEPTION, SkillName.STEALTH},
        "tool_proficiencies": {},
        "languages": {},
        "equipment": {},
    },
    Background.FOLK_HERO: {
        "skill_proficiencies": {SkillName.ANIMAL_HANDLING, SkillName.SURVIVAL},
        "tool_proficiencies": {},
        "languages": {},
        "equipment": {},
    },
    Background.NOBLE: {
        "skill_proficiencies": {SkillName.HISTORY, SkillName.PERSUASION},
        "tool_proficiencies": {},
        "languages": {},
        "equipment": {},
    },
    Background.SAGE: {
        "skill_proficiencies": {SkillName.ARCANA, SkillName.HISTORY},
        "tool_proficiencies": {},
        "languages": {},
        "equipment": {},
    },
    Background.SOLDIER: {
        "skill_proficiencies": {SkillName.ATHLETICS, SkillName.INTIMIDATION},
        "tool_proficiencies": {},
        "languages": {},
        "equipment": {},
    },
}
