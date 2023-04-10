from django.db import models

import game.models as gmodels


class Message(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    character = models.ForeignKey(
        gmodels.Character, on_delete=models.SET_NULL, null=True
    )
    content = models.CharField(max_length=200)
