from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from ..constants.conditions import ConditionName


class Condition(models.Model):
    """Reference model for D&D 5e SRD conditions."""

    name = models.CharField(
        max_length=15, choices=ConditionName.choices, primary_key=True
    )
    description = models.TextField(max_length=1000)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return str(self.get_name_display())


class CharacterCondition(models.Model):
    """Tracks conditions currently affecting a character."""

    character = models.ForeignKey(
        "character.Character",
        on_delete=models.CASCADE,
        related_name="active_conditions",
    )
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE)
    # For Exhaustion (1-6), null for other conditions
    exhaustion_level = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(6)],
    )

    class Meta:
        unique_together = ["character", "condition"]
        verbose_name_plural = "character conditions"

    def __str__(self):
        if self.condition.name == ConditionName.EXHAUSTION:
            return f"{self.condition} (Level {self.exhaustion_level})"
        return str(self.condition)
