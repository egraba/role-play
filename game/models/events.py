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
        return self.message


class Quest(Event):
    content = models.CharField(max_length=1000)

    def __str__(self):
        return self.content


class Request(Event):
    class Status(models.TextChoices):
        PENDING = "P", "Pending"
        DONE = "D", "Done"

    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=Status, default=Status.PENDING)

    class Meta:
        abstract = True


class AbilityCheckRequest(Request):
    class DifficultyClass(models.IntegerChoices):
        VERY_EASY = 5, "Very easy"
        EASY = 10, "Easy"
        MEDIUM = 15, "Medium"
        HARD = 20, "Hard"
        VERY_HARD = 25, "Very hard"
        NEARLY_IMPOSSIBLE = 30, "Nearly impossible"

    ability_type = models.ForeignKey(AbilityType, on_delete=models.CASCADE)
    difficulty_class = models.SmallIntegerField(choices=DifficultyClass)


class Action(Event):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    result = models.BooleanField()

    class Meta:
        abstract = True


class AbilityCheck(Action):
    ability_check_request = models.ForeignKey(
        AbilityCheckRequest, on_delete=models.CASCADE
    )
