from django.contrib.auth.models import User
from django.db import models
from django.db.models.functions import Upper
from django.urls import reverse
from django.utils import timezone
from django_fsm import FSMField, transition

from character.models.character import Character
from master.models import Campaign
from ..constants.game import GameStatus


class Game(models.Model):
    name = models.CharField(max_length=100)
    campaign = models.ForeignKey(
        Campaign, on_delete=models.SET_NULL, null=True, blank=True
    )
    start_date = models.DateTimeField(null=True, blank=True)
    status = FSMField(
        max_length=1, choices=GameStatus.choices, default=GameStatus.UNDER_PREPARATION
    )

    class Meta:
        indexes = [
            models.Index(Upper("name"), name="game_name_upper_idx"),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("game", args=(self.id,))

    def can_start(self):
        return self.player_set.count() >= 2

    @transition(
        field=status,
        source=GameStatus.UNDER_PREPARATION,
        target=GameStatus.ONGOING,
        conditions=[can_start],
    )
    def start(self):
        self.start_date = timezone.now()

    def is_under_preparation(self):
        return self.status == GameStatus.UNDER_PREPARATION

    def is_ongoing(self):
        return self.status == GameStatus.ONGOING


class Master(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.OneToOneField(Game, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Player(models.Model):
    character = models.OneToOneField(Character, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return self.character.user.username
