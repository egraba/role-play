from django.db import models

from ..constants.abilities import AbilityName
from ..constants.equipment import (
    ArmorName,
    ArmorType,
    GearName,
    GearType,
    PackName,
    ToolName,
    ToolType,
    WeaponName,
    WeaponType,
)
from ..exceptions import EquipmentDoesNotExist
from ..utils.equipment.parsers import parse_ac_settings, parse_strength


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


class WeaponSettings(models.Model):
    name = models.CharField(max_length=30, primary_key=True, choices=WeaponName.choices)
    weapon_type = models.CharField(max_length=2, choices=WeaponType.choices)

    class Meta:
        verbose_name_plural = "weapon settings"

    def __str__(self):
        return str(self.name)


class Weapon(models.Model):
    settings = models.ForeignKey(WeaponSettings, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.settings.name)


class PackSettings(models.Model):
    name = models.CharField(max_length=30, primary_key=True, choices=PackName.choices)

    def __str__(self):
        return str(self.name)


class Pack(models.Model):
    settings = models.ForeignKey(PackSettings, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.settings.name)


class Inventory(models.Model):
    capacity = models.SmallIntegerField(default=0)
    gp = models.SmallIntegerField(default=0)
    armor = models.ForeignKey(Armor, null=True, on_delete=models.SET_NULL)

    def _compute_ac(self):
        """
        Compute character's Armor Class (AC) depending on the selected armor.
        """
        base_ac, is_dex_modifier, modifier_max, bonus = parse_ac_settings(
            self.armor.settings.ac
        )
        self.character.ac = base_ac + bonus
        if is_dex_modifier:
            dex_modifier = self.character.abilities.get(
                ability_type=AbilityName.DEXTERITY
            ).modifier
            self.character.ac += max(dex_modifier, modifier_max)

    def _reduce_speed(self):
        """
        Reduce character's speed depending on the selected armor.
        """
        max_strength = parse_strength(self.armor.settings.strength)
        strength = self.character.abilities.get(ability_type=AbilityName.STRENGTH).score
        if strength < max_strength:
            self.character.speed -= 10

    def _add_armor(self, name: str) -> None:
        """
        Add an armor to the inventory.
        """
        self.armor = Armor.objects.create(settings=ArmorSettings.objects.get(name=name))
        self._compute_ac()
        self._reduce_speed()

    def _add_weapon(self, name: str) -> None:
        """
        Add a weapon to the inventory.
        """
        self.weapon = Weapon.objects.create(
            settings=WeaponSettings.objects.get(name=name)
        )

    def add(self, name: str) -> None:
        """
        Add an equipment to the inventory.
        """
        if (name, name) in ArmorName.choices:
            self._add_armor(name)
        elif (name, name) in WeaponName.choices:
            self._add_weapon(name)
        else:
            raise EquipmentDoesNotExist

    def contains(self, name: str, quantity: int = 1) -> bool:
        """
        Check if the inventory contains an equipment.
        """
        if self.armor.settings.name == name:
            return True
        return False


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
