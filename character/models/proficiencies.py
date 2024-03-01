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

    def __str__(self):
        return str(self.armor)


class WeaponProficiency(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "weapons proficiencies"

    def __str__(self):
        return str(self.weapon)


class ToolProficiency(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "tools proficiencies"

    def __str__(self):
        return str(self.tool)


class SavingThrowProficiency(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    ability_type = models.ForeignKey(AbilityType, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "saving throws proficiencies"

    def __str__(self):
        return str(self.ability_type)


class SkillProficiency(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "skills proficiencies"

    def __str__(self):
        return str(self.skill)
