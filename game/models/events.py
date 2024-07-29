from abc import abstractmethod

from django.db import models
from model_utils.managers import InheritanceManager

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
    """
    Events are everything that occur in a game.

    This class shall not be instantiated explicitly.
    """

    objects = InheritanceManager()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["-date"]),
        ]

    @abstractmethod
    def get_message(self):
        """
        Retrieve messages of an event.

        Messages represent "logs" of an event.
        Messages are not stored in database, only event content is.
        """
        pass


class GameStart(Event):
    def get_message(self):
        return "the game started."


class CharacterInvitation(Event):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)

    def get_message(self):
        return f"{self.character} was added to the game."


class Message(Event):
    content = models.CharField(max_length=100)

    def __str__(self):
        return self.content


class QuestUpdate(Event):
    content = models.CharField(max_length=1000)

    def __str__(self):
        return self.content


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


class CombatInitialization(Event):
    pass
