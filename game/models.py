from django.db import models

class Game(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True)

class Master(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)

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
