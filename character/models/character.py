from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db.models.functions import Upper
from django.urls import reverse

from utils.dice import Dice

from .abilities import Ability
from .advancement import Advancement
from .classes import Class, Proficiencies
from .equipment import Inventory
from .races import Alignment, Language, Race, Sense, Size
from .skills import Skill


class Character(models.Model):
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
    xp = models.IntegerField(default=0)
    hp = models.SmallIntegerField(default=100)
    max_hp = models.SmallIntegerField(default=100)
    proficiency_bonus = models.SmallIntegerField(default=2)
    skills = models.ManyToManyField(Skill)
    abilities = models.ManyToManyField(Ability)
    gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.MALE)
    ac = models.SmallIntegerField(default=0)
    adult_age = models.SmallIntegerField(null=True, blank=True)
    life_expectancy = models.SmallIntegerField(null=True, blank=True)
    alignment = models.CharField(
        max_length=1, choices=Alignment.choices, null=True, blank=True
    )
    size = models.CharField(max_length=1, choices=Size.choices, null=True, blank=True)
    speed = models.SmallIntegerField(null=True, blank=True)
    languages = models.ManyToManyField(Language)
    senses = models.ManyToManyField(Sense)
    hit_dice = models.CharField(max_length=5, default="1d8")
    hp_increase = models.SmallIntegerField(default=0)
    proficiencies = models.OneToOneField(
        Proficiencies, on_delete=models.SET_NULL, blank=True, null=True
    )
    inventory = models.OneToOneField(
        Inventory, on_delete=models.CASCADE, blank=True, null=True
    )

    class Meta:
        indexes = [
            models.Index(Upper("name"), name="character_name_upper_idx"),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("character-detail", args=(self.id,))

    def _check_level_increase(self):
        next_level = self.level + 1
        advancement = cache.get(f"advancement_{next_level}")
        if not advancement:
            cache.set(f"advancement_{next_level}", advancement)
            advancement = Advancement.objects.get(level=next_level)
        if self.xp >= advancement.xp:
            return True
        return False

    def _increase_level(self):
        self.level += 1
        advancement = cache.get(f"advancement_{self.level}")
        if not advancement:
            advancement = Advancement.objects.get(level=self.level)
            cache.set(f"advancement_{self.level}", advancement)
        self.proficiency_bonus += advancement.proficiency_bonus

        # Increase hit dice
        self.hit_dice = Dice(self.hit_dice).add_throws(1)

        # Increase HP
        self.max_hp += self.hp_increase

    def increase_xp(self, xp):
        self.xp += xp
        while self._check_level_increase():
            self._increase_level()
