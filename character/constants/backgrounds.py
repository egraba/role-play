from django.db.models import TextChoices

from equipment.constants.equipment import ToolName
from .feats import FeatName
from .skills import SkillName


class Background(TextChoices):
    ACOLYTE = "acolyte", "Acolyte"
    CRIMINAL = "criminal", "Criminal"
    SAGE = "sage", "Sage"
    SOLDIER = "soldier", "Soldier"


BACKGROUNDS: dict = {
    Background.ACOLYTE: {
        "skill_proficiencies": {SkillName.INSIGHT, SkillName.RELIGION},
        "tool_proficiency": ToolName.CALLIGRAPHERS_SUPPLIES,
        "origin_feat": FeatName.MAGIC_INITIATE_CLERIC,
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
        "ideals": {
            1: "Tradition. The ancient traditions of worship and sacrifice must be preserved and upheld. (Lawful)",
            2: "Charity. I always try to help those in need, no matter what the personal cost. (Good)",
            3: "Change. We must help bring about the changes the gods are constantly working in the world. (Chaotic)",
            4: "Power. I hope to one day rise to the top of my faith's religious hierarchy. (Lawful)",
            5: "Faith. I trust that my deity will guide my actions. I have faith that if I work hard, things will go well. (Lawful)",
            6: "Aspiration. I seek to prove myself worthy of my god's favor by matching my actions against his or her teachings. (Any)",
        },
        "bonds": {
            1: "I would die to recover an ancient relic of my faith that was lost long ago.",
            2: "I will someday get revenge on the corrupt temple hierarchy who branded me a heretic.",
            3: "I owe my life to the priest who took me in when my parents died.",
            4: "Everything I do is for the common people.",
            5: "I will do anything to protect the temple where I served.",
            6: "I seek to preserve a sacred text that my enemies consider heretical and seek to destroy.",
        },
        "flaws": {
            1: "I judge others harshly, and myself even more severely.",
            2: "I put too much trust in those who wield power within my temple's hierarchy.",
            3: "My piety sometimes leads me to blindly trust those that profess faith in my god.",
            4: "I am inflexible in my thinking.",
            5: "I am suspicious of strangers and expect the worst of them.",
            6: "Once I pick a goal, I become obsessed with it to the detriment of everything else in my life.",
        },
    },
    Background.CRIMINAL: {
        "skill_proficiencies": {SkillName.SLEIGHT_OF_HAND, SkillName.STEALTH},
        "tool_proficiency": ToolName.THIEVES_TOOLS,
        "origin_feat": FeatName.ALERT,
        "personality_traits": {
            1: "I always have a plan for what to do when things go wrong.",
            2: "I am always calm, no matter what the situation. I never raise my voice or let my emotions control me.",
            3: "The first thing I do in a new place is note the locations of everything valuable - or where such things could be hidden.",
            4: "I would rather make a new friend than a new enemy.",
            5: "I am incredibly slow to trust. Those who seem the fairest often have the most to hide.",
            6: "I don't pay attention to the risks in a situation. Never tell me the odds.",
            7: "The best way to get me to do something is to tell me I can't do it.",
            8: "I blow up at the slightest insult.",
        },
        "ideals": {
            1: "Honor. I don't steal from others in the trade. (Lawful)",
            2: "Freedom. Chains are meant to be broken, as are those who would forge them. (Chaotic)",
            3: "Charity. I steal from the wealthy so that I can help people in need. (Good)",
            4: "Greed. I will do whatever it takes to become wealthy. (Evil)",
            5: "People. I'm loyal to my friends, not to any ideals, and everyone else can take a trip down the Styx for all I care. (Neutral)",
            6: "Redemption. There's a spark of good in everyone. (Good)",
        },
        "bonds": {
            1: "I'm trying to pay off an old debt I owe to a generous benefactor.",
            2: "My ill-gotten gains go to support my family.",
            3: "Something important was taken from me, and I aim to steal it back.",
            4: "I will become the greatest thief that ever lived.",
            5: "I'm guilty of a terrible crime. I hope I can redeem myself for it.",
            6: "Someone I loved died because of I mistake I made. That will never happen again.",
        },
        "flaws": {
            1: "When I see something valuable, I can't think about anything but how to steal it.",
            2: "When faced with a choice between money and my friends, I usually choose the money.",
            3: "If there's a plan, I'll forget it. If I don't forget it, I'll ignore it.",
            4: "I have a 'tell' that reveals when I'm lying.",
            5: "I turn tail and run when things look bad.",
            6: "An innocent person is in prison for a crime that I committed. I'm okay with that.",
        },
    },
    Background.SAGE: {
        "skill_proficiencies": {SkillName.ARCANA, SkillName.HISTORY},
        "tool_proficiency": ToolName.CALLIGRAPHERS_SUPPLIES,
        "origin_feat": FeatName.MAGIC_INITIATE_WIZARD,
        "personality_traits": {
            1: "I use polysyllabic words that convey the impression of great erudition.",
            2: "I've read every book in the world's greatest libraries - or I like to boast that I have.",
            3: "I'm used to helping out those who aren't as smart as I am, and I patiently explain anything and everything to others.",
            4: "There's nothing I like more than a good mystery.",
            5: "I'm willing to listen to every side of an argument before I make my own judgment.",
            6: "I . . . speak . . . slowly . . . when talking . . . to idiots, . . . which . . . almost . . . everyone . . . is . . . compared . . . to me.",
            7: "I am horribly, horribly awkward in social situations.",
            8: "I'm convinced that people are always trying to steal my secrets.",
        },
        "ideals": {
            1: "Knowledge. The path to power and self-improvement is through knowledge. (Neutral)",
            2: "Beauty. What is beautiful points us beyond itself toward what is true. (Good)",
            3: "Logic. Emotions must not cloud our logical thinking. (Lawful)",
            4: "No Limits. Nothing should fetter the infinite possibility inherent in all existence. (Chaotic)",
            5: "Power. Knowledge is the path to power and domination. (Evil)",
            6: "Self-Improvement. The goal of a life of study is the betterment of oneself. (Any)",
        },
        "bonds": {
            1: "It is my duty to protect my students.",
            2: "I have an ancient text that holds terrible secrets that must not fall into the wrong hands.",
            3: "I work to preserve a library, university, scriptorium, or monastery.",
            4: "My life's work is a series of tomes related to a specific field of lore.",
            5: "I've been searching my whole life for the answer to a certain question.",
            6: "I sold my soul for knowledge. I hope to do great deeds and win it back.",
        },
        "flaws": {
            1: "I am easily distracted by the promise of information.",
            2: "Most people scream and run when they see a demon. I stop and take notes on its anatomy.",
            3: "Unlocking an ancient mystery is worth the price of a civilization.",
            4: "I overlook obvious solutions in favor of complicated ones.",
            5: "I speak without really thinking through my words, invariably insulting others.",
            6: "I can't keep a secret to save my life, or anyone else's.",
        },
    },
    Background.SOLDIER: {
        "skill_proficiencies": {SkillName.ATHLETICS, SkillName.INTIMIDATION},
        "tool_proficiency": None,  # Gaming set choice - handled in form
        "origin_feat": FeatName.SAVAGE_ATTACKER,
        "personality_traits": {
            1: "I'm always polite and respectful.",
            2: "I'm haunted by memories of war. I can't get the images of violence out of my mind.",
            3: "I've lost too many friends, and I'm slow to make new ones.",
            4: "I'm full of inspiring and cautionary tales from my military experience relevant to almost every combat situation.",
            5: "I can stare down a hell hound without flinching.",
            6: "I enjoy being strong and like breaking things.",
            7: "I have a crude sense of humor.",
            8: "I face problems head-on. A simple, direct solution is the best path to success.",
        },
        "ideals": {
            1: "Greater Good. Our lot is to lay down our lives in defense of others. (Good)",
            2: "Responsibility. I do what I must and obey just authority. (Lawful)",
            3: "Independence. When people follow orders blindly, they embrace a kind of tyranny. (Chaotic)",
            4: "Might. In life as in war, the stronger force wins. (Evil)",
            5: "Live and Let Live. Ideals aren't worth killing over or going to war for. (Neutral)",
            6: "Nation. My city, nation, or people are all that matter. (Any)",
        },
        "bonds": {
            1: "I would still lay down my life for the people I served with.",
            2: "Someone saved my life on the battlefield. To this day, I will never leave a friend behind.",
            3: "My honor is my life.",
            4: "I'll never forget the crushing defeat my company suffered or the enemies who dealt it.",
            5: "Those who fight beside me are those worth dying for.",
            6: "I fight for those who cannot fight for themselves.",
        },
        "flaws": {
            1: "The monstrous enemy we faced in battle still leaves me quivering with fear.",
            2: "I have little respect for anyone who is not a proven warrior.",
            3: "I made a terrible mistake in battle that cost many lives - and I would do anything to keep that mistake secret.",
            4: "My hatred of my enemies is blind and unreasoning.",
            5: "I obey the law, even if the law causes misery.",
            6: "I'd rather eat my armor than admit when I'm wrong.",
        },
    },
}
