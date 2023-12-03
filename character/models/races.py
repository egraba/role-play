from django.db import models


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


class RacialTrait(models.Model):
    race = models.CharField(max_length=1, choices=Race.choices, unique=True)
    adult_age = models.SmallIntegerField()
    life_expectancy = models.SmallIntegerField()
    alignment = models.CharField(max_length=1, choices=Alignment.choices)
    size = models.CharField(max_length=1, choices=Size.choices)
    speed = models.SmallIntegerField()
    languages = models.ManyToManyField(Language)
    abilities = models.ManyToManyField(Ability)

    def __str__(self):
        return f"{self.get_race_display()} racial trait"


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
