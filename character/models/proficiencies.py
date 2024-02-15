from django.db import models

from .abilities import AbilityType
from .character import Character
from .equipment import Armor, Tool, Weapon
from .skills import Skill


class ArmorProficiency(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    armor = models.ForeignKey(Armor, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "armor proficiencies"


class WeaponsProficiency(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "weapons proficiencies"


class ToolsProficiency(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "tools proficiencies"


class SavingThrowProficiency(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    ability_type = models.ForeignKey(AbilityType, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "saving throws proficiencies"


class SkillsProficiency(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "skills proficiencies"
