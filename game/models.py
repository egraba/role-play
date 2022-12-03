from django.db import models

class Game(models.Model):
    start_date = models.DateTimeField()
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
    name = models.CharField(max_length=255)
    race = models.CharField(max_length=1, choices=RACES)
    age = models.SmallIntegerField()
    xp = models.SmallIntegerField(default=0)
    mp = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.name

class Narrative(models.Model):
    date = models.DateTimeField()
    message = models.CharField(max_length=1024)
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