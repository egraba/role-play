from django.db.models import IntegerChoices, TextChoices


class EventType(TextChoices):
    MESSAGE = "message"
    GAME_START = "game.start"
    QUEST_UPDATE = "quest.update"
    ABILITY_CHECK_REQUEST = "ability.check.request"
    ABILITY_CHECK = "ability.check"
    ABILITY_CHECK_RESULT = "ability.check.result"
    SAVING_THROW_REQUEST = "saving.throw.request"
    SAVING_THROW = "saving.throw"
    SAVING_THROW_RESULT = "saving.throw.result"
    COMBAT_INITIATION = "combat.initiation"


class RollStatus(TextChoices):
    PENDING = "P", "Pending"
    DONE = "D", "Done"


class DifficultyClass(IntegerChoices):
    VERY_EASY = 5, "Very easy"
    EASY = 10, "Easy"
    MEDIUM = 15, "Medium"
    HARD = 20, "Hard"
    VERY_HARD = 25, "Very hard"
    NEARLY_IMPOSSIBLE = 30, "Nearly impossible"


class RollType(IntegerChoices):
    ABILITY_CHECK = 1, "Ability check"
    SAVING_THROW = 2, "Saving throw"
    ATTACK = 3, "Attack"


class Against(TextChoices):
    BEING_FRIGHTENED = "F", "Being frightened"
    CHARM = "C", "Charm"
    POISON = "P", "Poison"


class RollResult(TextChoices):
    SUCCESS = "S", "Success"
    FAILURE = "F", "Failure"
