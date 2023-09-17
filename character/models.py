from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db.models.functions import Upper
from django.urls import reverse


class Advancement(models.Model):
    xp = models.IntegerField()
    level = models.SmallIntegerField(primary_key=True)
    proficiency_bonus = models.SmallIntegerField()

    class Meta:
        ordering = ["xp"]

    def __str__(self):
        return str(self.level)


class Race(models.TextChoices):
    HUMAN = "H", "Human"
    HALFLING = "G", "Halfling"
    ELF = "E", "Elf"
    DWARF = "D", "Dwarf"


class Alignment(models.TextChoices):
    LAWFUL = "L", "Lawful"
    FREEDOM = "F", "Freedom"
    NONE = "N", "None"


class Size(models.TextChoices):
    SMALL = "S", "Small"
    MEDIUM = "M", "Medium"


class Language(models.Model):
    class Name(models.TextChoices):
        COMMON = "C", "Common"
        DWARVISH = "D", "Dwarvish"
        ELVISH = "E", "Elvish"
        HALFLING = "H", "Halfling"

    name = models.CharField(max_length=1, choices=Name.choices, unique=True)

    def __str__(self):
        return self.name


class Ability(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.TextField(max_length=50)

    class Meta:
        verbose_name_plural = "abilities"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Class(models.TextChoices):
    CLERIC = "C", "Cleric"
    FIGHTER = "F", "Fighter"
    ROGUE = "R", "Rogue"
    WIZARD = "W", "Wizard"


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
    strength = models.SmallIntegerField(default=0)
    dexterity = models.SmallIntegerField(default=0)
    constitution = models.SmallIntegerField(default=0)
    intelligence = models.SmallIntegerField(default=0)
    wisdom = models.SmallIntegerField(default=0)
    charisma = models.SmallIntegerField(default=0)
    strength_modifier = models.SmallIntegerField(default=0)
    dexterity_modifier = models.SmallIntegerField(default=0)
    constitution_modifier = models.SmallIntegerField(default=0)
    intelligence_modifier = models.SmallIntegerField(default=0)
    wisdom_modifier = models.SmallIntegerField(default=0)
    charisma_modifier = models.SmallIntegerField(default=0)
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
    abilities = models.ManyToManyField(Ability)

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
            advancement = Advancement.objects.get(level=next_level)
            cache.set(f"advancement_{next_level}", advancement)
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

    def increase_xp(self, xp):
        self.xp += xp
        while self._check_level_increase():
            self._increase_level()


class Inventory(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    capacity = models.SmallIntegerField(default=0)
    gp = models.SmallIntegerField(default=0)


class Equipment(models.Model):
    name = models.CharField(max_length=20)
    inventory = models.ForeignKey(
        Inventory, on_delete=models.SET_NULL, null=True, blank=True
    )
    weight = models.SmallIntegerField()

    def __str__(self):
        return self.name


class RacialTrait(models.Model):
    race = models.CharField(max_length=1, choices=Race.choices, unique=True)
    adult_age = models.SmallIntegerField()
    life_expectancy = models.SmallIntegerField()
    alignment = models.CharField(max_length=1, choices=Alignment.choices)
    size = models.CharField(max_length=1, choices=Size.choices)
    speed = models.SmallIntegerField()
    languages = models.ManyToManyField(Language)
    abilities = models.ManyToManyField(Ability)


class AbilityScoreIncrease(models.Model):
    class Ability(models.TextChoices):
        STRENGTH = "strength"
        DEXTERITY = "dexterity"
        CONSTITUTION = "constitution"
        INTELLIGENCE = "intelligence"
        WISDOM = "wisdom"
        CHARISMA = "charisma"

    racial_trait = models.ForeignKey(RacialTrait, on_delete=models.CASCADE)
    ability = models.CharField(max_length=20, choices=Ability.choices)
    increase = models.SmallIntegerField()


class Proficiency(models.Model):
    armor = models.TextField(max_length=50)
    weapons = models.TextField(max_length=50)
    tools = models.TextField(max_length=50)
    saving_throws = models.TextField(max_length=50)
    skills = models.TextField(max_length=50)


class ClassFeature(models.Model):
    class_name = models.CharField(max_length=1, choices=Class.choices, unique=True)
    hit_dice = models.CharField(max_length=5)
    hp_first_level = models.SmallIntegerField()
    hp_higher_levels = models.SmallIntegerField()
    proficiencies = models.ManyToManyField(Proficiency)
    equipment = models.ManyToManyField(Equipment)


class ClassAdvancement(models.Model):
    class_name = models.CharField(max_length=1, choices=Class.choices)
    level = models.SmallIntegerField()
    proficiency_bonus = models.SmallIntegerField()

    class Meta:
        ordering = ["class_name"]

    def __str__(self):
        return str(self.level)
