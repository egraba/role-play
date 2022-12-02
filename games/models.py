from django.db import models

class Game(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

class Master(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)

class Character(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    race = models.SmallIntegerField()
    age = models.SmallIntegerField()
    xp = models.SmallIntegerField()
    mp = models.SmallIntegerField()
