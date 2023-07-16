from django.db import models
from django.db.models.functions import Upper
from django.urls import reverse


class Character(models.Model):
    class Race(models.TextChoices):
        HUMAN = "H", "Human"
        ORC = "O", "Orc"
        ELF = "E", "Elf"
        DWARF = "D", "Dwarf"

    name = models.CharField(max_length=100, unique=True)
    race = models.CharField(max_length=1, choices=Race.choices)
    xp = models.SmallIntegerField(default=0)
    hp = models.SmallIntegerField(default=100)
    max_hp = models.SmallIntegerField(default=100)

    class Meta:
        indexes = [
            models.Index(Upper("name"), name="character_name_upper_idx"),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("character-detail", args=(self.id,))
