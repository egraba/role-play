from django.db import models

from .game import Game, Player


class Combat(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)


class Round(models.Model):
    combat = models.ForeignKey(Combat, on_delete=models.CASCADE)


class Turn(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
