from django.db import models

from ..constants.skills import SkillName
from .abilities import AbilityType


class Skill(models.Model):
    name = models.CharField(max_length=20, primary_key=True, choices=SkillName)
    ability_type = models.ForeignKey(AbilityType, on_delete=models.CASCADE)
    description = models.TextField(max_length=1000)

    def __str__(self):
        return str(self.name)
