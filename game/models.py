from django.db import models
from django.utils import timezone


class Game(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Character(models.Model):
    RACES = (("H", "Human"), ("O", "Orc"), ("E", "Elf"), ("D", "Dwarf"))
    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    race = models.CharField(max_length=1, choices=RACES)
    xp = models.SmallIntegerField(default=0)
    hp = models.SmallIntegerField(default=100)
    max_hp = models.SmallIntegerField(default=100)

    def __str__(self):
        return self.name


class Narrative(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    message = models.CharField(max_length=1000)

    def __str__(self):
        return self.message


class PendingAction(models.Model):
    ACTION_TYPES = (
        ("D", "Launch dice"),
        ("C", "Make choice"),
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE, blank=False)
    narrative = models.ForeignKey(Narrative, on_delete=models.CASCADE, blank=False)
    character = models.ForeignKey(Character, on_delete=models.CASCADE, blank=False)
    action_type = models.CharField(max_length=1, choices=ACTION_TYPES, blank=False)

    def __str__(self):
        return self.action_type


class Action(Narrative):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class DiceLaunch(Action):
    score = models.SmallIntegerField()

    def __str__(self):
        return self.score


class Choice(Action):
    selection = models.CharField(max_length=255)

    def __str__(self):
        return self.selection
