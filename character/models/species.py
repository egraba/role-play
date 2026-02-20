from django.db import models

from ..constants.races import Size
from ..constants.species import SpeciesName, SpeciesTraitName


class SpeciesTrait(models.Model):
    """Species traits from D&D 2024 SRD."""

    name = models.CharField(
        max_length=30, choices=SpeciesTraitName.choices, primary_key=True
    )
    description = models.TextField(max_length=500)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return str(self.get_name_display())


class Species(models.Model):
    """D&D 2024 SRD species."""

    name = models.CharField(
        max_length=20, choices=SpeciesName.choices, primary_key=True
    )
    size = models.CharField(max_length=1, choices=Size.choices)
    speed = models.PositiveSmallIntegerField(default=30)
    darkvision = models.PositiveSmallIntegerField(default=0)  # 0 = none
    traits = models.ManyToManyField(SpeciesTrait)
    languages = models.ManyToManyField("character.Language")
    description = models.TextField(max_length=1000, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "species"

    def __str__(self):
        return str(self.get_name_display())
