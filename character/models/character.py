from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db.models.functions import Upper
from django.urls import reverse

from character.models.advancement import Advancement
from character.models.classes import Class, Proficiencies
from character.models.equipment import Inventory
from character.models.races import Alignment, Language, Race, RacialTrait, Sense, Size
from utils.dice import Dice


class AbilityType(models.Model):
    class Name(models.TextChoices):
        STRENGTH = "STR", "Strength"
        DEXTERITY = "DEX", "Dexterity"
        CONSTITUTION = "CON", "Constitution"
        INTELLIGENCE = "INT", "Intelligence"
        WISDOM = "WIS", "Wisdom"
        CHARISMA = "CHA", "Charisma"

    name = models.CharField(max_length=3, primary_key=True, choices=Name)
    description = models.TextField(max_length=1000)

    def __str__(self):
        return self.name


class Ability(models.Model):
    ability_type = models.ForeignKey(AbilityType, on_delete=models.CASCADE)
    score = models.SmallIntegerField()
    modifier = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name_plural = "abilities"

    def __str__(self):
        return self.ability_type


class AbilityScoreIncrease(models.Model):
    racial_trait = models.ForeignKey(RacialTrait, on_delete=models.CASCADE)
    ability = models.ForeignKey(AbilityType, on_delete=models.CASCADE)
    increase = models.SmallIntegerField()


class Skill(models.Model):
    class Name(models.TextChoices):
        ATHLETICS = "Athletics"
        ACROBATICS = "Acrobatics"
        SLEIGHT_OF_HAND = "Sleight of Hand"
        STEALTH = "Stealth"
        ARCANA = "Arcana"
        HISTORY = "History"
        INVESTIGATION = "Investigation"
        NATURE = "Nature"
        RELIGION = "Religion"
        ANIMAL_HANDLING = "Animal Handling"
        INSIGHT = "Insight"
        MEDICINE = "Medicine"
        PERCEPTION = "Perception"
        SURVIVAL = "Survival"
        DECEPTION = "Deception"
        INTIMIDATION = "Intimidation"
        PERFORMANCE = "Performance"
        PERSUASION = "Persuasion"

    name = models.CharField(max_length=20, primary_key=True, choices=Name)
    ability = models.ForeignKey(AbilityType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


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
