from django.db import models

from ..constants.races import LanguageName, LanguageType


class Language(models.Model):
    name = models.CharField(max_length=11, choices=LanguageName.choices, unique=True)
    language_type = models.CharField(max_length=1, choices=LanguageType.choices)
    script = models.CharField(
        max_length=11, choices=LanguageName.choices, blank=True, null=True
    )

    def __str__(self):
        return str(self.name)
