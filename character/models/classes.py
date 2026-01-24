from django.db import models

from character.constants.classes import ClassName


class Class(models.Model):
    """D&D 2024 SRD character class."""

    name = models.CharField(max_length=20, choices=ClassName.choices, primary_key=True)
    description = models.TextField(max_length=1000, blank=True)

    # Hit Points
    hit_die = models.PositiveSmallIntegerField()  # 6, 8, 10, or 12
    hp_first_level = models.PositiveSmallIntegerField()
    hp_higher_levels = models.PositiveSmallIntegerField()

    # Primary Ability (for multiclassing prereqs, etc.)
    primary_ability = models.ForeignKey(
        "AbilityType",
        on_delete=models.PROTECT,
        related_name="primary_for_classes",
    )

    # Saving Throw Proficiencies
    saving_throws = models.ManyToManyField(
        "AbilityType", related_name="classes_proficient"
    )

    # Armor & Weapon Proficiencies (categories stored as JSON lists)
    armor_proficiencies = models.JSONField(default=list)
    weapon_proficiencies = models.JSONField(default=list)

    # Starting Equipment
    starting_wealth_dice = models.CharField(max_length=10)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "classes"

    def __str__(self) -> str:
        return str(self.get_name_display())


class ClassFeature(models.Model):
    """Feature gained by a class at a specific level."""

    name = models.CharField(max_length=50)
    klass = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="features")
    level = models.PositiveSmallIntegerField()
    description = models.TextField(max_length=2000)

    class Meta:
        ordering = ["klass", "level", "name"]
        unique_together = ["klass", "name"]

    def __str__(self) -> str:
        return f"{self.name} (Level {self.level})"


class CharacterClass(models.Model):
    """Junction table for Character-Class relationship (supports multiclassing)."""

    character = models.ForeignKey(
        "Character", on_delete=models.CASCADE, related_name="character_classes"
    )
    klass = models.ForeignKey(Class, on_delete=models.PROTECT)
    level = models.PositiveSmallIntegerField(default=1)
    is_primary = models.BooleanField(default=True)

    class Meta:
        unique_together = ["character", "klass"]

    def __str__(self) -> str:
        return f"{self.character.name}: {self.klass.name} {self.level}"


class CharacterFeature(models.Model):
    """Junction table tracking class features gained by a character."""

    character = models.ForeignKey(
        "Character", on_delete=models.CASCADE, related_name="class_features"
    )
    class_feature = models.ForeignKey(
        ClassFeature, on_delete=models.CASCADE, related_name="character_instances"
    )
    source_class = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name="granted_features"
    )
    level_gained = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ["character", "class_feature"]
        ordering = ["source_class", "level_gained", "class_feature__name"]

    def __str__(self) -> str:
        return f"{self.character.name}: {self.class_feature.name}"
