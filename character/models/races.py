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
        BRAVE = "BR", "Brave"
        DARKVISION = "DV", "Darkvision"
        DWARVEN_COMBAT_TRAINING = "DC", "Dwarven Combat Training"
        DWARVEN_RESILIENCE = "DR", "Dwarven Resilience"
        FEY_ANCESTRY = "FA", "Fey Ancestry"
        HALFLING_NIMBLENESS = "HN", "Halfling Nimbleness"
        KEEN_SENSES = "KS", "Keen Senses"
        LUCKY = "LU", "Lucky"
        STONECUNNING = "SC", "Stonecunning"
        TOOL_PROFICIENCY = "TP", "Tool Proficiency"
        TRANCE = "TR", "Trance"

    name = models.CharField(max_length=30, choices=Name.choices, unique=True)
    description = models.TextField(max_length=50)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return str(self.name)
