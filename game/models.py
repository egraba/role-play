from django.contrib.auth.models import User
from django.db import models
from django.db.models.functions import Upper
from django.urls import reverse
from django.utils import timezone
from django_fsm import FSMField, transition

import character.models as cmodels
import master.models as mmodels


class Game(models.Model):
    class Status(models.TextChoices):
        UNDER_PREPARATION = "P", "Under preparation"
        ONGOING = "O", "Ongoing"
        FINISHED = "F", "Finished"

    name = models.CharField(max_length=50, unique=True)
    story = models.ForeignKey(
        mmodels.Story, on_delete=models.SET_NULL, null=True, blank=True
    )
    master = models.OneToOneField(mmodels.Master, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = FSMField(
        max_length=1, choices=Status.choices, default=Status.UNDER_PREPARATION
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
        number_of_players = Player.objects.filter(game=self).count()
        return number_of_players >= 2

    @transition(
        field=status,
        source=Status.UNDER_PREPARATION,
        target=Status.ONGOING,
        conditions=[can_start],
    )
    def start(self):
        self.start_date = timezone.now()

    @transition(field=status, source=Status.ONGOING, target=Status.FINISHED)
    def end(self):
        self.end_date = timezone.now()
        for player in Player.objects.filter(game=self):
            player.game = None
            player.save()

    def is_under_preparation(self):
        return self.status == self.Status.UNDER_PREPARATION

    def is_ongoing(self):
        return self.status == self.Status.ONGOING

    def is_finished(self):
        return self.status == self.Status.FINISHED


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    character = models.OneToOneField(cmodels.Character, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Event(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    message = models.CharField(max_length=100)

    class Meta:
        indexes = [
            models.Index(fields=["-date"]),
        ]

    def __str__(self):
        return self.message


class Tale(Event):
    content = models.CharField(max_length=1000)

    def __str__(self):
        return self.content


class PendingAction(Event):
    class ActionType(models.TextChoices):
        LAUNCH_DICE = "D", "Launch dice"
        MAKE_CHOICE = "C", "Make choice"

    character = models.OneToOneField(cmodels.Character, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=1, choices=ActionType.choices)

    def __str__(self):
        return self.action_type


class Action(Event):
    character = models.ForeignKey(cmodels.Character, on_delete=models.CASCADE)

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
