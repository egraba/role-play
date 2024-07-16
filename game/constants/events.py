from django.db.models import IntegerChoices, TextChoices


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


class RollResultType(TextChoices):
    SUCCESS = "S", "Success"
    FAILURE = "F", "Failure"
