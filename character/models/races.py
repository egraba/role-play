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
        return str(self.name)


class Sense(models.Model):
    class Name(models.TextChoices):
        DARKVISION = "DV", "Darkvision"
        DWARVEN_RESILIENCE = "DR", "Dwarven Resilience"
        DWARVEN_COMBAT_TRAINING = "DC", "Dwarven Combat Training"
        TOOL_PROFICIENCY = "TP", "Tool Proficiency"
        STONECUNNING = "SC", "Stonecunning"
        KEEN_SENSES = "KS", "Keen Senses"
        FEY_ANCESTRY = "FA", "Fey Ancestry"
        TRANCE = "TR", "Trance"
        LUCKY = "LU", "Lucky"
        BRAVE = "BR", "Brave"
        HALFLING_NIMBLENESS = "HN", "Halfling Nimbleness"

    name = models.CharField(max_length=30, choices=Name.choices, unique=True)
    description = models.TextField(max_length=50)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return str(self.name)


class RacialTrait(models.Model):
    race = models.CharField(max_length=1, choices=Race.choices, unique=True)
    adult_age = models.SmallIntegerField()
    life_expectancy = models.SmallIntegerField()
    alignment = models.CharField(max_length=1, choices=Alignment.choices)
    size = models.CharField(max_length=1, choices=Size.choices)
    speed = models.SmallIntegerField()
    languages = models.ManyToManyField(Language)
    senses = models.ManyToManyField(Sense)

    def __str__(self):
        return f"{self.get_race_display()} racial trait"
