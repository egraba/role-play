from django.db import models

from ..constants.equipment import (
    WeaponName,
    WeaponType,
    ArmorName,
    ArmorType,
    GearName,
    GearType,
    ToolName,
    ToolType,
    PackName,
)


class Inventory(models.Model):
    capacity = models.SmallIntegerField(default=0)
    gp = models.SmallIntegerField(default=0)


class Equipment(models.Model):
    name = models.CharField(max_length=30)
    inventory = models.ForeignKey(
        Inventory, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return str(self.name)


class Weapon(models.Model):
    name = models.CharField(max_length=30, primary_key=True, choices=WeaponName.choices)
    weapon_type = models.CharField(max_length=2, choices=WeaponType.choices)

    def __str__(self):
        return str(self.name)


class Armor(models.Model):
    name = models.CharField(max_length=30, primary_key=True, choices=ArmorName.choices)
    armor_type = models.CharField(max_length=2, choices=ArmorType.choices)

    def __str__(self):
        return str(self.name)


class Pack(models.Model):
    name = models.CharField(max_length=30, primary_key=True, choices=PackName.choices)

    def __str__(self):
        return str(self.name)


class Gear(models.Model):
    name = models.CharField(max_length=30, primary_key=True, choices=GearName.choices)
    gear_type = models.CharField(
        max_length=2, choices=GearType.choices, default=GearType.MISC
    )

    def __str__(self):
        return str(self.name)


class Tool(models.Model):
    name = models.CharField(max_length=30, primary_key=True, choices=ToolName.choices)
    tool_type = models.CharField(
        max_length=2, choices=ToolType.choices, default=ToolType.MISC
    )

    def __str__(self):
        return str(self.name)
