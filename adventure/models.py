from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from .constants import Region, SceneType, Tone


class Campaign(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="campaigns",
    )
    synopsis = models.TextField(max_length=3000, blank=True)
    main_conflict = models.TextField(max_length=1000, blank=True)
    objective = models.TextField(max_length=500, blank=True)
    party_level = models.SmallIntegerField(default=1)
    tone = models.CharField(max_length=10, choices=Tone, default=Tone.HEROIC)
    setting = models.TextField(max_length=1000, blank=True)

    def __str__(self) -> str:
        return str(self.title)

    def get_absolute_url(self) -> str:
        return reverse("adventure:campaign-detail", kwargs={"slug": self.slug})

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Act(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="acts"
    )
    title = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=1)
    summary = models.TextField(max_length=2000, blank=True)
    goal = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return str(self.title)


class Scene(models.Model):
    act = models.ForeignKey(Act, on_delete=models.CASCADE, related_name="scenes")
    title = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=1)
    scene_type = models.CharField(
        max_length=1, choices=SceneType, default=SceneType.EXPLORATION
    )
    description = models.TextField(max_length=3000, blank=True)
    hook = models.TextField(max_length=500, blank=True)
    resolution = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return str(self.title)


class NPC(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="npcs"
    )
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, blank=True)
    motivation = models.TextField(max_length=500, blank=True)
    personality = models.TextField(max_length=500, blank=True)
    appearance = models.TextField(max_length=500, blank=True)
    stat_block = models.ForeignKey(
        "bestiary.MonsterSettings",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="npcs",
    )
    notes = models.TextField(max_length=1000, blank=True)

    def __str__(self) -> str:
        return str(self.name)


class Location(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="locations"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=2000, blank=True)
    region = models.CharField(max_length=10, choices=Region, default=Region.DUNGEON)
    connections = models.ManyToManyField("self", blank=True)

    def __str__(self) -> str:
        return str(self.name)
