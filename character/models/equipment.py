from django.db import models

from utils.lists import item_in_choices

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


class Inventory(models.Model):
    capacity = models.SmallIntegerField(default=0)
    gp = models.SmallIntegerField(default=0)

    def _compute_ac(self, armor):
        """
        Compute character's Armor Class (AC) depending on the selected armor.
        """
        base_ac, is_dex_modifier, modifier_max, bonus = parse_ac_settings(
            armor.settings.ac
        )
        self.character.ac = base_ac + bonus
        if is_dex_modifier:
            dex_modifier = self.character.abilities.get(
                ability_type=AbilityName.DEXTERITY
            ).modifier
            self.character.ac += max(dex_modifier, modifier_max)

    def _reduce_speed(self, armor):
        """
        Reduce character's speed depending on the selected armor.
        """
        max_strength = parse_strength(armor.settings.strength)
        strength = self.character.abilities.get(ability_type=AbilityName.STRENGTH).score
        if strength < max_strength:
            self.character.speed -= 10

    def _add_armor(self, name: str) -> None:
        armor = Armor.objects.create(
            settings=ArmorSettings.objects.get(name=name), inventory=self
        )
        self._compute_ac(armor)
        self._reduce_speed(armor)

    def _add_weapon(self, name: str) -> None:
        Weapon.objects.create(
            settings=WeaponSettings.objects.get(name=name), inventory=self
        )

    def _add_pack(self, name: str) -> None:
        Pack.objects.create(
            settings=PackSettings.objects.get(name=name), inventory=self
        )

    def _add_gear(self, name: str) -> None:
        Gear.objects.create(
            settings=GearSettings.objects.get(name=name), inventory=self
        )

    def _add_tool(self, name: str) -> None:
        Tool.objects.create(
            settings=ToolSettings.objects.get(name=name), inventory=self
        )

    def add(self, name: str) -> None:
        """
        Add an equipment to the inventory.
        """
        if item_in_choices(name, ArmorName.choices):
            self._add_armor(name)
        elif item_in_choices(name, WeaponName.choices):
            self._add_weapon(name)
        elif item_in_choices(name, PackName.choices):
            self._add_pack(name)
        elif item_in_choices(name, GearName.choices):
            self._add_gear(name)
        elif item_in_choices(name, ToolName.choices):
            self._add_tool(name)
        else:
            raise EquipmentDoesNotExist

    def contains(self, name: str, quantity: int = 1) -> bool:
        """
        Check if the inventory contains an equipment.
        """
        if self.armor_set.filter(settings__name=name).count() == quantity:
            return True
        if self.weapon_set.filter(settings__name=name).count() == quantity:
            return True
        if self.pack_set.filter(settings__name=name).count() == quantity:
            return True
        if self.gear_set.filter(settings__name=name).count() == quantity:
            return True
        if self.tool_set.filter(settings__name=name).count() == quantity:
            return True
        return False


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
    """Concrete armor"""

    settings = models.ForeignKey(ArmorSettings, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.SET_NULL, null=True)

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
    """Concrete weapon"""

    settings = models.ForeignKey(WeaponSettings, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.settings.name)


class PackSettings(models.Model):
    name = models.CharField(max_length=30, primary_key=True, choices=PackName.choices)

    class Meta:
        verbose_name_plural = "pack settings"

    def __str__(self):
        return str(self.name)


class Pack(models.Model):
    """Concrete pack"""

    settings = models.ForeignKey(PackSettings, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.settings.name)


class GearSettings(models.Model):
    name = models.CharField(max_length=30, primary_key=True, choices=GearName.choices)
    gear_type = models.CharField(
        max_length=2, choices=GearType.choices, default=GearType.MISC
    )

    class Meta:
        verbose_name_plural = "gear settings"

    def __str__(self):
        return str(self.name)


class Gear(models.Model):
    """Concrete gear"""

    settings = models.ForeignKey(GearSettings, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.settings.name)


class ToolSettings(models.Model):
    name = models.CharField(max_length=30, primary_key=True, choices=ToolName.choices)
    tool_type = models.CharField(
        max_length=2, choices=ToolType.choices, default=ToolType.MISC
    )

    class Meta:
        verbose_name_plural = "tool settings"

    def __str__(self):
        return str(self.name)


class Tool(models.Model):
    """Concrete tool"""

    settings = models.ForeignKey(ToolSettings, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.settings.name)
