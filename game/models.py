from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_fsm import FSMField, transition


class Game(models.Model):
    STATUSES = (("P", "Under preparation"), ("O", "Ongoing"), ("F", "Finished"))
    name = models.CharField(max_length=50)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = FSMField(max_length=1, choices=STATUSES, default="P")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("game", args=(self.id,))

    def can_start(self):
        number_of_characters = Character.objects.filter(game=self).count()
        return number_of_characters >= 2

    @transition(field=status, source="P", target="O", conditions=[can_start])
    def start(self):
        self.start_date = timezone.now()

    @transition(field=status, source="O", target="F")
    def end(self):
        self.end_date = timezone.now()
        for character in Character.objects.filter(game=self):
            character.game = None
            character.save()

    def is_ongoing(self):
        return self.status == "O"


class Character(models.Model):
    RACES = (("H", "Human"), ("O", "Orc"), ("E", "Elf"), ("D", "Dwarf"))
    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    race = models.CharField(max_length=1, choices=RACES)
    xp = models.SmallIntegerField(default=0)
    hp = models.SmallIntegerField(default=100)
    max_hp = models.SmallIntegerField(default=100)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


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
    ACTION_TYPES = (
        ("D", "Launch dice"),
        ("C", "Make choice"),
    )
    character = models.OneToOneField(Character, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=1, choices=ACTION_TYPES)

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
