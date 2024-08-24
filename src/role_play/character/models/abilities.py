from django.db import models
from ..constants.abilities import AbilityName


class AbilityType(models.Model):
    name = models.CharField(max_length=3, primary_key=True, choices=AbilityName)
    description = models.TextField(max_length=1000)

    def __str__(self):
        return str(self.name)


class Ability(models.Model):
    ability_type = models.ForeignKey(AbilityType, on_delete=models.CASCADE)
    score = models.SmallIntegerField()
    modifier = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name_plural = "abilities"

    def __str__(self):
        return str(self.ability_type.name)
