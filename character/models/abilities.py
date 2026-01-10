from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from ..ability_modifiers import compute_ability_modifier
from ..constants.abilities import AbilityName


class AbilityType(models.Model):
    name = models.CharField(max_length=3, primary_key=True, choices=AbilityName)
    description = models.TextField(max_length=1000)

    def __str__(self):
        return str(self.name)


class Ability(models.Model):
    ability_type = models.ForeignKey(AbilityType, on_delete=models.CASCADE)
    score = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    modifier = models.SmallIntegerField(default=0, editable=False)

    class Meta:
        verbose_name_plural = "abilities"

    def __str__(self):
        return str(self.ability_type.name)

    def save(self, *args, **kwargs):
        self.modifier = compute_ability_modifier(self.score)
        super().save(*args, **kwargs)
