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

    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        UNDEFINED = "U", "Undefined"

    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    race = models.CharField(max_length=1, choices=Race.choices)
    class_name = models.CharField(
        max_length=1, choices=Class.choices, verbose_name="class"
    )
    level = models.SmallIntegerField(default=1)
    xp = models.SmallIntegerField(default=0)
    hp = models.SmallIntegerField(default=100)
    max_hp = models.SmallIntegerField(default=100)
    proficiency_bonus = models.SmallIntegerField(default=2)
    strength = models.SmallIntegerField(default=0)
    dexterity = models.SmallIntegerField(default=0)
    constitution = models.SmallIntegerField(default=0)
    intelligence = models.SmallIntegerField(default=0)
    wisdom = models.SmallIntegerField(default=0)
    charisma = models.SmallIntegerField(default=0)
    gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.MALE)
    ac = models.SmallIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(Upper("name"), name="character_name_upper_idx"),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("character-detail", args=(self.id,))


class Advancement(models.Model):
    xp = models.SmallIntegerField()
    level = models.SmallIntegerField(unique=True)
    proficiency_bonus = models.SmallIntegerField()

    def __str__(self):
        return str(self.level)


class Inventory(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    capacity = models.SmallIntegerField(default=0)
    gp = models.SmallIntegerField(default=0)


class Equipment(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=20)
    inventory = models.ForeignKey(
        Inventory, on_delete=models.SET_NULL, null=True, blank=True
    )
    weight = models.SmallIntegerField()

    def __str__(self):
        return self.name


class Weapon(Equipment):
    class Distance(models.TextChoices):
        MELEE = "M", "Melee"
        RANGED = "R", "Ranged"

    distance = models.CharField(max_length=1, choices=Distance.choices)
