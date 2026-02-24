from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from .constants import Tone


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
