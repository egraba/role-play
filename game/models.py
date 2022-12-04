from django.db import models
from django.utils import timezone

class Game(models.Model):
    start_date = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=255, null=False, blank=False)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class Character(models.Model):
    RACES = (
        ('H', 'Human'),
        ('O', 'Orc'),
        ('E', 'Elf'),
        ('D', 'Dwarf')
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    race = models.CharField(max_length=1, choices=RACES, null=False, blank=False)
    age = models.SmallIntegerField(null=False, blank=False)
    xp = models.SmallIntegerField(default=0)
    hp = models.SmallIntegerField(default=100)
    max_hp = models.SmallIntegerField(default=100)

    def __str__(self):
        return self.name

class Narrative(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField(default=timezone.now)
    message = models.CharField(max_length=1024, null=False, blank=False)
    action_required = models.BooleanField(default=False)

    def __str(self):
        return self.message

class Action(models.Model):
    ACTIONS = (
        ('D', 'Launch dice'),
    )
    date = models.DateTimeField()
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    action = models.CharField(max_length=1, choices=ACTIONS)
    result = models.SmallIntegerField()

class DiceLaunch(models.Model):
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    score = models.SmallIntegerField()
