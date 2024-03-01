from django.db import models

from .equipment import Equipment


class Klass(models.TextChoices):
    CLERIC = "C", "Cleric"
    FIGHTER = "F", "Fighter"
    ROGUE = "R", "Rogue"
    WIZARD = "W", "Wizard"


class KlassFeature(models.Model):
    klass = models.CharField(max_length=1, choices=Klass.choices, unique=True)
    equipment = models.ManyToManyField(Equipment)

    def __str__(self):
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

    def __str__(self):
        return f"{self.klass_feature} hit points"


class KlassAdvancement(models.Model):
    klass = models.CharField(max_length=1, choices=Klass.choices)
    level = models.SmallIntegerField()
    proficiency_bonus = models.SmallIntegerField()

    class Meta:
        ordering = ["klass"]

    def __str__(self):
        return str(self.level)
