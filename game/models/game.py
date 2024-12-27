from django.conf import settings
from django.db import models
from django.db.models.functions import Upper
from django.urls import reverse

from character.models.character import Character
from master.models import Campaign

from ..constants.game import GameState


class Game(models.Model):
    name = models.CharField(max_length=100)
    campaign = models.ForeignKey(
        Campaign, on_delete=models.SET_NULL, null=True, blank=True
    )
    start_date = models.DateTimeField(null=True, blank=True)
    state = models.CharField(
        max_length=1, choices=GameState.choices, default=GameState.UNDER_PREPARATION
    )

    class Meta:
        indexes = [
            models.Index(Upper("name"), name="game_name_upper_idx"),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("game", args=(self.id,))


class Quest(models.Model):
    environment = models.TextField(max_length=3000)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return self.environment[:10]


class Master(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.OneToOneField(Game, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Player(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    character = models.OneToOneField(Character, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
