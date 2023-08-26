from django.contrib.auth.models import User
from django.db import models
from django.db.models.functions import Upper
from django.urls import reverse


class Character(models.Model):
    class Race(models.TextChoices):
        HUMAN = "H", "Human"
        HALFLING = "G", "Halfling"
        ELF = "E", "Elf"
        DWARF = "D", "Dwarf"

    class Class(models.TextChoices):
        FIGHTER = "F", "Fighter"

    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    race = models.CharField(max_length=1, choices=Race.choices)
    class_name = models.CharField(max_length=1, choices=Class.choices)
    level = models.SmallIntegerField(default=1)
    xp = models.SmallIntegerField(default=0)
    hp = models.SmallIntegerField(default=100)
    max_hp = models.SmallIntegerField(default=100)
    proficiency_bonus = models.SmallIntegerField(default=2)

    class Meta:
        indexes = [
            models.Index(Upper("name"), name="character_name_upper_idx"),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("character-detail", args=(self.id,))
