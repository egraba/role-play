from django.db import models

from ..constants.abilities import AbilityName
from ..constants.equipment import (
    ArmorName,
    ArmorType,
    Disadvantage,
    GearName,
    GearType,
    PackName,
    ToolName,
    ToolType,
    WeaponName,
    WeaponType,
)
from ..exceptions import EquipmentDoesNotExist
from ..models.disadvantages import (
    AbilityCheckDisadvantage,
    AttackRollDisadvantage,
    SavingThrowDisadvantage,
    SpellCastDisadvantage,
)
from ..models.proficiencies import ArmorProficiency
from ..utils.equipment_parsers import parse_ac_settings, parse_strength


class Inventory(models.Model):
    capacity = models.SmallIntegerField(default=0)
    gp = models.SmallIntegerField(default=0)

    def _compute_ac(self, armor) -> None:
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
            if modifier_max > 0 and dex_modifier > modifier_max:
                self.character.ac += modifier_max
            else:
                self.character.ac += dex_modifier

    def _reduce_speed(self, armor) -> None:
        """
        Reduce character's speed depending on the selected armor.
        """
        max_strength = parse_strength(armor.settings.strength)
        strength = self.character.abilities.get(ability_type=AbilityName.STRENGTH).score
        if strength < max_strength:
            self.character.speed -= 10

    def _set_disadvantage(self, armor) -> None:
        """
        Set disadvantage on dexterity rolls depending on the selected armor.
        """
        if not ArmorProficiency.objects.get(
            character=self.character, armor=armor
        ).exists():
            for ability_name in AbilityName.choices:
                AbilityCheckDisadvantage.objects.create(
                    character=self.character, ability_type__name=ability_name
                )
            SavingThrowDisadvantage.objects.create(character=self.character)
            AttackRollDisadvantage.objects.create(
                character=self.character, ability_type__name=AbilityName.STRENGTH
            )
            AttackRollDisadvantage.objects.create(
                character=self.character, ability_type__name=AbilityName.DEXTERITY
            )
            SpellCastDisadvantage.objects.create(character=self.character)
        if armor.settings.stealth == Disadvantage.DISADVANTAGE:
            AbilityCheckDisadvantage.objects.create(
                character=self.character, ability_type__name=AbilityName.DEXTERITY
            )

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
        if name in ArmorName.values:
            self._add_armor(name)
        elif name in WeaponName.values:
            self._add_weapon(name)
        elif name in PackName.values:
            self._add_pack(name)
        elif name in GearName.values:
            self._add_gear(name)
        elif name in ToolName.values:
            self._add_tool(name)
        else:
            raise EquipmentDoesNotExist

    def contains(self, name: str, quantity: int = 1) -> bool:
        """
        Check if the inventory contains an equipment, with at least
        the specified quantity.
        """
        if self.armor_set.filter(settings__name=name).count() >= quantity:
            return True
        if self.weapon_set.filter(settings__name=name).count() >= quantity:
            return True
        if self.pack_set.filter(settings__name=name).count() >= quantity:
            return True
        if self.gear_set.filter(settings__name=name).count() >= quantity:
            return True
        if self.tool_set.filter(settings__name=name).count() >= quantity:
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
    cost = models.SmallIntegerField()
    damage = models.CharField(max_length=15, null=True)
    weight = models.SmallIntegerField()
    properties = models.CharField(max_length=60, null=True)

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
