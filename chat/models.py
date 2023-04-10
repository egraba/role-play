from django.contrib.auth.models import User
from django.db import models

import game.models as gmodels


class Room(models.Model):
    game = models.OneToOneField(gmodels.Game, on_delete=models.CASCADE)


class Message(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=200)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
