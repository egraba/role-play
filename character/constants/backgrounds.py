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
        "personality_traits": {
            1: "I idolize a particular hero of my faith, and constantly refer to that person's deeds and example.",
            2: "I can find common ground between the fiercest enemies, empathizing with them and always working toward peace.",
            3: "I see omens in every event and action. The gods try to speak to us, we just need to listen.",
            4: "Nothing can shake my optimistic attitude.",
            5: "I quote (or misquote) sacred texts and proverbs in almost every situation.",
            6: "I am tolerant (or intolerant) of other faiths and respect (or condemn) the worship of other gods.",
            7: "I've enjoyed fine food, drink, and high society among my temple's elite. Rough living grates on me.",
            8: "I've spent so long in the temple that I have little practical experience dealing with people in the outside world.",
        },
        "bond": {
            1: "I would die to recover an ancient relic of my faith that was lost long ago.",
            2: "I will someday get revenge on the corrupt temple hierarchy who branded me a heretic.",
            3: "I owe my life to the priest who took me in when my parents died.",
            4: "Everything I do is for the common people.",
            5: "I will do anything to protect the temple where I served.",
            6: "I seek to preserve a sacred text that my enemies consider heretical and seek to destroy.",
        },
        "flaw": {
            1: "I judge others harshly, and myself even more severely.",
            2: "I put too much trust in those who wield power within my temple's hierarchy.",
            3: "My piety sometimes leads me to blindly trust those that profess faith in my god.",
            4: "I am inflexible in my thinking.",
            5: "I am suspicious of strangers and expect the worst of them.",
            6: "Once I pick a goal, I become obsessed with it to the detriment of everything else in my life.",
        },
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
