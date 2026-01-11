from django.db import models

from character.constants.klasses import ClassName


class Klass(models.TextChoices):
    """Legacy enum for backwards compatibility during migration."""

    CLERIC = "C", "Cleric"
    FIGHTER = "F", "Fighter"
    ROGUE = "R", "Rogue"
    WIZARD = "W", "Wizard"


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


# Legacy models - kept for migration compatibility
class KlassFeature(models.Model):
    klass = models.CharField(max_length=1, choices=Klass.choices, unique=True)

    def __str__(self) -> str:
        return f"{self.get_klass_display()}'s feature"


class HitPoints(models.Model):
    klass_feature = models.OneToOneField(
        KlassFeature, on_delete=models.SET_NULL, blank=True, null=True
    )
    hit_dice = models.CharField(max_length=5)
    hp_first_level = models.SmallIntegerField()
    hp_higher_levels = models.SmallIntegerField()

    class Meta:
        verbose_name_plural = "hit points"

    def __str__(self) -> str:
        return f"{self.klass_feature} hit points"


class KlassAdvancement(models.Model):
    klass = models.CharField(max_length=1, choices=Klass.choices)
    level = models.SmallIntegerField()
    proficiency_bonus = models.SmallIntegerField()

    class Meta:
        ordering = ["klass"]

    def __str__(self) -> str:
        return str(self.level)
