from django.db import models

from character.models.abilities import AbilityType
from character.models.character import Character

from .game import Game


class Event(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=100)

    class Meta:
        indexes = [
            models.Index(fields=["-date"]),
        ]

    def __str__(self):
        return str(self.message)


class Quest(Event):
    content = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.content)


class RollRequest(Event):
    class Status(models.TextChoices):
        PENDING = "P", "Pending"
        DONE = "D", "Done"

    class DifficultyClass(models.IntegerChoices):
        VERY_EASY = 5, "Very easy"
        EASY = 10, "Easy"
        MEDIUM = 15, "Medium"
        HARD = 20, "Hard"
        VERY_HARD = 25, "Very hard"
        NEARLY_IMPOSSIBLE = 30, "Nearly impossible"

    class RollType(models.IntegerChoices):
        ABILITY_CHECK = 1, "Ability check"
        SAVING_THROW = 2, "Saving throw"
        ATTACK = 3, "Attack"

    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=Status, default=Status.PENDING)
    ability_type = models.ForeignKey(AbilityType, on_delete=models.CASCADE)
    difficulty_class = models.SmallIntegerField(choices=DifficultyClass)
    roll_type = models.SmallIntegerField(choices=RollType)


class Roll(Event):
    class Result(models.TextChoices):
        SUCCESS = "S", "Success"
        FAILURE = "F", "Failure"

    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    request = models.ForeignKey(RollRequest, on_delete=models.CASCADE)
    result = models.CharField(max_length=1, choices=Result)
