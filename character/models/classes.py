from django.db import models

from .equipment import Equipment


class Class(models.TextChoices):
    CLERIC = "C", "Cleric"
    FIGHTER = "F", "Fighter"
    ROGUE = "R", "Rogue"
    WIZARD = "W", "Wizard"


class ClassFeature(models.Model):
    class_name = models.CharField(max_length=1, choices=Class.choices, unique=True)
    equipment = models.ManyToManyField(Equipment)

    def __str__(self):
        return f"{self.get_class_name_display()}'s feature"


class HitPoints(models.Model):
    class_feature = models.OneToOneField(
        ClassFeature, on_delete=models.SET_NULL, blank=True, null=True
    )
    hit_dice = models.CharField(max_length=5)
    hp_first_level = models.SmallIntegerField()
    hp_higher_levels = models.SmallIntegerField()

    class Meta:
        verbose_name_plural = "hit points"

    def __str__(self):
        return f"{self.class_feature} hit points"


class ClassAdvancement(models.Model):
    class_name = models.CharField(max_length=1, choices=Class.choices)
    level = models.SmallIntegerField()
    proficiency_bonus = models.SmallIntegerField()

    class Meta:
        ordering = ["class_name"]

    def __str__(self):
        return str(self.level)
