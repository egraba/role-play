from django.db import models

from .abilities import AbilityType


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
    ability_type = models.ForeignKey(AbilityType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
