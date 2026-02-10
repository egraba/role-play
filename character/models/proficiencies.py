from django.db import models


class ArmorProficiency(models.Model):
    character = models.ForeignKey("character.Character", on_delete=models.CASCADE)
    armor = models.ForeignKey("equipment.ArmorSettings", on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "armor proficiencies"

    def __str__(self):
        return str(self.armor)


class WeaponProficiency(models.Model):
    character = models.ForeignKey("character.Character", on_delete=models.CASCADE)
    weapon = models.ForeignKey("equipment.WeaponSettings", on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "weapons proficiencies"

    def __str__(self):
        return str(self.weapon)


class ToolProficiency(models.Model):
    character = models.ForeignKey("character.Character", on_delete=models.CASCADE)
    tool = models.ForeignKey("equipment.ToolSettings", on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "tools proficiencies"

    def __str__(self):
        return str(self.tool)


class SavingThrowProficiency(models.Model):
    character = models.ForeignKey("character.Character", on_delete=models.CASCADE)
    ability_type = models.ForeignKey("character.AbilityType", on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "saving throws proficiencies"

    def __str__(self):
        return str(self.ability_type)


class SkillProficiency(models.Model):
    character = models.ForeignKey("character.Character", on_delete=models.CASCADE)
    skill = models.ForeignKey("character.Skill", on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "skills proficiencies"

    def __str__(self):
        return str(self.skill)
