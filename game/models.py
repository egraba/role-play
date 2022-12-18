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
    
    def __str(self):
        return self.message

class ActionRequest(models.Model):
    ACTION_TYPES = (
        ('C', 'Make choice'),
        ('D', 'Launch dice'),
    )
    narrative = models.ForeignKey(Narrative, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=1, choices=ACTION_TYPES)

class ActionResponse(models.Model):
    narrative = models.ForeignKey(Narrative, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)

    class Meta:
        abstract = True

class Choice(ActionResponse):
    selection = models.CharField(max_length=255)

class DiceLaunch(ActionResponse):
    score = models.SmallIntegerField()
