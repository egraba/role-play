from django.contrib.auth.models import User
from django.db import models
from django.db.models.functions import Upper
from django.urls import reverse
from django.utils import timezone
from django_fsm import FSMField, transition


class Game(models.Model):
    class Status(models.TextChoices):
        UNDER_PREPARATION = "P", "Under preparation"
        ONGOING = "O", "Ongoing"
        FINISHED = "F", "Finished"

    name = models.CharField(max_length=50, unique=True)
    master = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
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
        number_of_characters = Character.objects.filter(game=self).count()
        return number_of_characters >= 2

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
        for character in Character.objects.filter(game=self):
            character.game = None
            character.save()

    def is_ongoing(self):
        return self.status == self.Status.ONGOING


class Character(models.Model):
    class Race(models.TextChoices):
        HUMAN = "H", "Human"
        ORC = "O", "Orc"
        ELF = "E", "Elf"
        DWARF = "D", "Dwarf"

    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    race = models.CharField(max_length=1, choices=Race.choices)
    xp = models.SmallIntegerField(default=0)
    hp = models.SmallIntegerField(default=100)
    max_hp = models.SmallIntegerField(default=100)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(Upper("name"), name="character_name_upper_idx"),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("character-detail", args=(self.id,))


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

    character = models.OneToOneField(Character, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=1, choices=ActionType.choices)

    def __str__(self):
        return self.action_type


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
