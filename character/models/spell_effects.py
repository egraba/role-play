"""Spell effect models for D&D 5e magic system.

This module defines:
- SpellEffectTemplate: Links spell settings to their mechanical effects
- ActiveSpellEffect: Tracks ongoing spell effects on characters
- SummonedCreature: Tracks creatures summoned by spells
"""

from django.db import models

from character.constants.spells import (
    EffectDurationType,
    SpellDamageType,
    SpellEffectType,
    SpellSaveEffect,
    SpellSaveType,
    SpellTargetType,
)


class SpellEffectTemplate(models.Model):
    """Links spell settings to their mechanical effects.

    One spell can have multiple effect templates (e.g., Fireball has damage,
    while Hold Person has both damage and condition effects).
    """

    spell = models.ForeignKey(
        "SpellSettings",
        on_delete=models.CASCADE,
        related_name="effect_templates",
    )
    effect_type = models.CharField(
        max_length=20,
        choices=SpellEffectType.choices,
    )
    target_type = models.CharField(
        max_length=20,
        choices=SpellTargetType.choices,
    )

    # Damage/Healing
    damage_type = models.CharField(
        max_length=20,
        choices=SpellDamageType.choices,
        blank=True,
    )
    base_dice = models.CharField(
        max_length=20,
        blank=True,
        help_text="Base damage/healing dice (e.g., '8d6')",
    )
    dice_per_level = models.CharField(
        max_length=20,
        blank=True,
        help_text="Additional dice per spell level above base (e.g., '1d6')",
    )

    # Saving throw
    save_type = models.CharField(
        max_length=5,
        choices=SpellSaveType.choices,
        default=SpellSaveType.NONE,
    )
    save_effect = models.CharField(
        max_length=15,
        choices=SpellSaveEffect.choices,
        default=SpellSaveEffect.NONE,
    )

    # Condition
    condition = models.ForeignKey(
        "Condition",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Condition applied by this effect",
    )

    # Buff/Debuff modifiers
    buff_description = models.TextField(
        blank=True,
        help_text="Description of the buff/debuff effect",
    )
    ac_modifier = models.SmallIntegerField(
        default=0,
        help_text="Modifier to AC (positive for buff, negative for debuff)",
    )
    attack_modifier = models.SmallIntegerField(
        default=0,
        help_text="Modifier to attack rolls",
    )
    damage_modifier = models.SmallIntegerField(
        default=0,
        help_text="Modifier to damage rolls",
    )

    # Area of Effect
    area_radius = models.PositiveSmallIntegerField(
        default=0,
        help_text="Radius in feet (0 for non-area effects)",
    )
    area_shape = models.CharField(
        max_length=20,
        blank=True,
        help_text="Shape of area (sphere, cube, cone, line)",
    )

    # Duration
    duration_type = models.CharField(
        max_length=20,
        choices=EffectDurationType.choices,
        default=EffectDurationType.INSTANTANEOUS,
    )
    duration_value = models.PositiveSmallIntegerField(
        default=0,
        help_text="Duration value (number of rounds, minutes, hours, etc.)",
    )

    class Meta:
        ordering = ["spell", "effect_type"]

    def __str__(self) -> str:
        return f"{self.spell.name}: {self.get_effect_type_display()}"


class ActiveSpellEffect(models.Model):
    """Tracks ongoing spell effects on characters.

    Used for buffs, debuffs, and concentration effects that persist
    beyond instantaneous resolution.
    """

    character = models.ForeignKey(
        "Character",
        on_delete=models.CASCADE,
        related_name="active_spell_effects",
    )
    template = models.ForeignKey(
        SpellEffectTemplate,
        on_delete=models.CASCADE,
    )
    caster = models.ForeignKey(
        "Character",
        on_delete=models.CASCADE,
        related_name="cast_effects",
    )
    rounds_remaining = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Rounds remaining (null for non-round durations)",
    )
    is_concentration = models.BooleanField(
        default=False,
        help_text="Whether this effect requires concentration",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.character.name}: {self.template.spell.name} effect"

    def decrement_rounds(self) -> bool:
        """Decrement rounds remaining. Returns True if effect should end."""
        if self.rounds_remaining is not None:
            self.rounds_remaining -= 1
            if self.rounds_remaining <= 0:
                return True
            self.save()
        return False

    def end_effect(self) -> None:
        """End this active spell effect."""
        self.delete()


class SummonedCreature(models.Model):
    """Tracks creatures summoned by spells.

    Summoned creatures exist for the spell's duration and may require
    concentration to maintain.
    """

    summoner = models.ForeignKey(
        "Character",
        on_delete=models.CASCADE,
        related_name="summoned_creatures",
    )
    spell = models.ForeignKey(
        "SpellSettings",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100)
    hp_current = models.PositiveIntegerField()
    hp_max = models.PositiveIntegerField()
    ac = models.PositiveSmallIntegerField()
    combat = models.ForeignKey(
        "game.Combat",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="summoned_creatures",
    )
    rounds_remaining = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Rounds remaining (null for non-round durations)",
    )
    is_concentration = models.BooleanField(
        default=False,
        help_text="Whether this summon requires concentration",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} (summoned by {self.summoner.name})"

    def take_damage(self, damage: int) -> int:
        """Apply damage to the summoned creature. Returns remaining HP."""
        self.hp_current = max(0, self.hp_current - damage)
        self.save()
        return self.hp_current

    def heal(self, amount: int) -> int:
        """Heal the summoned creature. Returns new HP."""
        self.hp_current = min(self.hp_max, self.hp_current + amount)
        self.save()
        return self.hp_current

    def is_alive(self) -> bool:
        """Check if the summoned creature is still alive."""
        return self.hp_current > 0

    def dismiss(self) -> None:
        """Dismiss the summoned creature."""
        self.delete()
