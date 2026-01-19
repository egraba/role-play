"""
Magic item models for D&D 5e SRD.

This module implements the magic item system including:
- MagicItemSettings: Reference data for magic item definitions
- MagicItem: Concrete magic items owned by characters
- Attunement: Tracking of character attunement to magic items (max 3)
"""

from django.core.exceptions import ValidationError
from django.db import models

from ..constants.magic_items import (
    MagicArmorBonus,
    MagicItemName,
    MagicItemType,
    MagicWeaponBonus,
    Rarity,
)


class MagicItemSettings(models.Model):
    """
    Reference data for magic item definitions from D&D 5e SRD.

    This model stores the template/definition for each magic item type.
    Individual instances of items are stored in MagicItem.
    """

    name = models.CharField(
        max_length=50, choices=MagicItemName.choices, primary_key=True
    )
    item_type = models.CharField(max_length=10, choices=MagicItemType.choices)
    rarity = models.CharField(max_length=15, choices=Rarity.choices)
    requires_attunement = models.BooleanField(default=False)
    attunement_requirement = models.CharField(
        max_length=100,
        blank=True,
        help_text="E.g., 'by a spellcaster', 'by a cleric or paladin'",
    )
    description = models.TextField(max_length=2000)

    # For +X weapons/armor, store the bonus
    bonus = models.CharField(
        max_length=2,
        choices=MagicWeaponBonus.choices + MagicArmorBonus.choices,
        blank=True,
    )

    # Mechanical effects stored as JSON for flexibility
    # Examples:
    # {"attack_bonus": 1, "damage_bonus": 1}  # +1 weapon
    # {"ac_bonus": 1}  # +1 armor
    # {"healing_dice": "2d4", "healing_bonus": 2}  # Potion of Healing
    # {"charges": 7, "recharge": "1d6+1"}  # Wand with charges
    effects = models.JSONField(default=dict, blank=True)

    # For consumables
    is_consumable = models.BooleanField(default=False)

    # Weight in pounds (0 for weightless items)
    weight = models.PositiveSmallIntegerField(default=0)

    # Cost in gold pieces (0 for priceless items)
    cost = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["rarity", "name"]
        verbose_name = "magic item settings"
        verbose_name_plural = "magic item settings"

    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"


class MagicItem(models.Model):
    """
    A concrete magic item in a character's possession.

    This represents an individual instance of a magic item that can be
    owned, traded, or attuned to by characters.
    """

    settings = models.ForeignKey(MagicItemSettings, on_delete=models.CASCADE)
    inventory = models.ForeignKey(
        "character.Inventory", on_delete=models.SET_NULL, null=True, blank=True
    )

    # For items with charges, track current charges
    current_charges = models.PositiveSmallIntegerField(null=True, blank=True)

    # Track if item has been identified
    is_identified = models.BooleanField(default=True)

    # For cursed items
    is_cursed = models.BooleanField(default=False)
    curse_revealed = models.BooleanField(default=False)

    # Notes about this specific item instance
    notes = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ["settings__name"]
        verbose_name = "magic item"
        verbose_name_plural = "magic items"

    def __str__(self):
        return str(self.settings.name)

    def save(self, *args, **kwargs):
        # Initialize charges from settings if not set
        if self.current_charges is None and self.settings.effects.get("charges"):
            self.current_charges = self.settings.effects["charges"]
        super().save(*args, **kwargs)

    @property
    def max_charges(self) -> int | None:
        """Get maximum charges from settings."""
        return self.settings.effects.get("charges")

    def use_charge(self, amount: int = 1) -> bool:
        """
        Use charges from this item.

        Returns True if successful, False if not enough charges.
        """
        if self.current_charges is None:
            return False
        if self.current_charges < amount:
            return False
        self.current_charges -= amount
        self.save()
        return True

    def recharge(self) -> int:
        """
        Recharge the item (typically at dawn).

        Returns the number of charges restored.
        """
        if self.current_charges is None or self.max_charges is None:
            return 0

        # Note: recharge_formula from settings.effects["recharge"] (e.g., "1d6+1")
        # would be used here with the dice rolling system in a full implementation
        restored = min(
            self.max_charges - self.current_charges,
            self.max_charges,  # Don't exceed max
        )
        self.current_charges = min(self.current_charges + restored, self.max_charges)
        self.save()
        return restored


class Attunement(models.Model):
    """
    Tracks a character's attunement to magic items.

    Per D&D 5e rules:
    - A character can attune to at most 3 magic items at a time
    - Attunement requires a short rest spent focusing on the item
    - Some items require attunement by specific classes or creature types
    """

    MAX_ATTUNEMENT_SLOTS = 3

    character = models.ForeignKey(
        "character.Character",
        on_delete=models.CASCADE,
        related_name="attunements",
    )
    magic_item = models.OneToOneField(
        MagicItem,
        on_delete=models.CASCADE,
        related_name="attunement",
    )
    attuned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["attuned_at"]
        verbose_name = "attunement"
        verbose_name_plural = "attunements"

    def __str__(self):
        return f"{self.character.name} attuned to {self.magic_item}"

    def clean(self):
        """Validate attunement constraints."""
        super().clean()

        # Check if item requires attunement
        if not self.magic_item.settings.requires_attunement:
            raise ValidationError(
                f"{self.magic_item.settings.name} does not require attunement."
            )

        # Check attunement slot limit (only for new attunements)
        if not self.pk:
            current_count = Attunement.objects.filter(character=self.character).count()
            if current_count >= self.MAX_ATTUNEMENT_SLOTS:
                raise ValidationError(
                    f"Cannot attune to more than {self.MAX_ATTUNEMENT_SLOTS} items. "
                    f"End attunement to another item first."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def attune(cls, character, magic_item) -> "Attunement":
        """
        Attune a character to a magic item.

        Raises ValidationError if attunement is not possible.
        """
        attunement = cls(character=character, magic_item=magic_item)
        attunement.save()
        return attunement

    def end_attunement(self) -> None:
        """End this attunement, freeing up a slot."""
        self.delete()

    @classmethod
    def get_attunement_count(cls, character) -> int:
        """Get the number of items a character is attuned to."""
        return cls.objects.filter(character=character).count()

    @classmethod
    def get_available_slots(cls, character) -> int:
        """Get the number of available attunement slots."""
        return cls.MAX_ATTUNEMENT_SLOTS - cls.get_attunement_count(character)
