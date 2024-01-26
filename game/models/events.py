from django.db import models

from character.models.character import Character

from .game import Game


class Event(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=100)

    class Meta:
        indexes = [
            models.Index(fields=["-date"]),
        ]

    def __str__(self):
        return self.message


class Quest(Event):
    content = models.CharField(max_length=1000)

    def __str__(self):
        return self.content


class Instruction(Event):
    content = models.TextField(max_length=1000)

    def __str__(self):
        return self.content


class Action(Event):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class XpIncrease(Action):
    xp = models.SmallIntegerField()

    def __str__(self):
        return str(self.xp)


class Damage(Action):
    hp = models.SmallIntegerField()

    def __str__(self):
        return str(self.hp)


class Healing(Action):
    hp = models.SmallIntegerField()

    def __str__(self):
        return str(self.hp)


class DiceLaunch(Action):
    score = models.SmallIntegerField()

    def __str__(self):
        return str(self.score)


class Choice(Action):
    selection = models.CharField(max_length=50)

    def __str__(self):
        return self.selection
