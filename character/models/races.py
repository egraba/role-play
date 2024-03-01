from django.db import models

from ..constants.races import LanguageName, SenseName


class Language(models.Model):
    name = models.CharField(max_length=1, choices=LanguageName.choices, unique=True)

    def __str__(self):
        return str(self.name)


class Sense(models.Model):
    name = models.CharField(max_length=30, choices=SenseName.choices, unique=True)
    description = models.TextField(max_length=50)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return str(self.name)
