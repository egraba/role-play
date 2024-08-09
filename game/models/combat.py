from django.db import models

from ..constants.combat import CombatAction
from .game import Game, Player


class Combat(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def get_initiative_order(self):
        """
        Collects all dexterity checks from fighters, sort them and return
        the order of turns during combat.
        """
        return [
            fighter for fighter in self.fighter_set.all().order_by("-dexterity_check")
        ]


class Round(models.Model):
    combat = models.ForeignKey(Combat, on_delete=models.CASCADE)


class Turn(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    move = models.IntegerField()
    action = models.CharField(choices=CombatAction)


class Fighter(models.Model):
    """
    A fighter represents a character during a combat.
    """

    character = models.ForeignKey("character.Character", on_delete=models.CASCADE)
    is_surprised = models.BooleanField(default=False)
    combat = models.ForeignKey(Combat, on_delete=models.CASCADE, null=True, blank=True)
    dexterity_check = models.SmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.character.name
