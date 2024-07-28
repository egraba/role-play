from django.db import models

from .game import Player
from ..constants.combat import CombatAction


class Combat(models.Model):
    pass


class Round(models.Model):
    combat = models.ForeignKey(Combat, on_delete=models.CASCADE)


class Turn(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    move = models.IntegerField()
    action = models.CharField(choices=CombatAction)


class Fighter(models.Model):
    character = models.ForeignKey("character.Character", on_delete=models.CASCADE)
    is_surprised = models.BooleanField(default=False)
    combat = models.ForeignKey(Combat, on_delete=models.CASCADE)
