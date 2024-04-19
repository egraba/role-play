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
from ..exceptions import EquipmentDoesNotExist


class ArmorSettings(models.Model):
    name = models.CharField(max_length=30, choices=ArmorName.choices, primary_key=True)
    armor_type = models.CharField(max_length=2, choices=ArmorType.choices)
    cost = models.SmallIntegerField()
    ac = models.CharField(max_length=25)
    strength = models.CharField(max_length=6, null=True, blank=True)
    stealth = models.CharField(max_length=1, null=True, blank=True)
    weight = models.SmallIntegerField()

    class Meta:
        verbose_name_plural = "armor settings"

    def __str__(self):
        return str(self.name)


class Armor(models.Model):
    settings = models.ForeignKey(ArmorSettings, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.settings.name)


class Inventory(models.Model):
    capacity = models.SmallIntegerField(default=0)
    gp = models.SmallIntegerField(default=0)
    armor = models.ForeignKey(Armor, null=True, on_delete=models.SET_NULL)

    def _add_armor(self, name: str) -> None:
        self.armor = Armor.objects.create(settings=ArmorSettings.get(name=name))

    def add(self, name: str) -> None:
        """
        Add an equipment to the inventory.
        """
        if name in ArmorName.choices:
            self._add_armor(name)
        else:
            raise EquipmentDoesNotExist

    def contains(self, name: str, quantity: int = 1) -> bool:
        """
        Check if the inventory contains an equipment.
        """
        if self.armor.settings.name == name:
            return True
        return False


class Weapon(models.Model):
    name = models.CharField(max_length=30, primary_key=True, choices=WeaponName.choices)
    weapon_type = models.CharField(max_length=2, choices=WeaponType.choices)

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
