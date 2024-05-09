from django.db import models

from .abilities import AbilityType


class AbilityCheckDisadvantage(models.Model):
    character = models.ForeignKey("character.Character", on_delete=models.CASCADE)
    ability_type = models.ForeignKey(AbilityType, on_delete=models.CASCADE)


class SavingThrowDisadvantage(models.Model):
    character = models.ForeignKey("character.Character", on_delete=models.CASCADE)


class AttackRollDisadvantage(models.Model):
    character = models.ForeignKey("character.Character", on_delete=models.CASCADE)
    ability_type = models.ForeignKey(AbilityType, on_delete=models.CASCADE)


class SpellCastDisadvantage(models.Model):
    character = models.ForeignKey("character.Character", on_delete=models.CASCADE)
