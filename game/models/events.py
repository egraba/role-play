from django.db import models

from character.constants.abilities import AbilityName
from character.models.character import Character

from ..constants.events import (
    Against,
    DifficultyClass,
    RollResult,
    RollStatus,
    RollType,
)
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
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1, choices=RollStatus, default=RollStatus.PENDING
    )
    ability_type = models.CharField(
        max_length=3,
        choices=AbilityName,
    )
    difficulty_class = models.SmallIntegerField(
        choices=DifficultyClass,
        blank=True,
        null=True,
    )
    roll_type = models.SmallIntegerField(choices=RollType)
    against = models.CharField(max_length=1, choices=Against, blank=True, null=True)
    is_combat = models.BooleanField(default=False)


class Roll(Event):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    request = models.ForeignKey(RollRequest, on_delete=models.CASCADE)
    result = models.CharField(max_length=1, choices=RollResult, blank=True, null=True)
