from django.db import models

from ..constants.feats import FeatName, FeatType


class Feat(models.Model):
    """D&D 2024 SRD feats."""

    name = models.CharField(max_length=30, choices=FeatName.choices, primary_key=True)
    feat_type = models.CharField(max_length=1, choices=FeatType.choices)
    description = models.TextField(max_length=1000)
    prerequisite = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return str(self.get_name_display())


class CharacterFeat(models.Model):
    """Junction table for Character-Feat relationship with metadata."""

    character = models.ForeignKey(
        "character.Character", on_delete=models.CASCADE, related_name="character_feats"
    )
    feat = models.ForeignKey(Feat, on_delete=models.CASCADE)
    granted_by = models.CharField(
        max_length=20, blank=True
    )  # "background", "species", "class"

    class Meta:
        unique_together = ["character", "feat"]

    def __str__(self):
        return f"{self.character.name}: {self.feat.name}"
