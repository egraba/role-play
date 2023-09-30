from django.db import models


class Advancement(models.Model):
    xp = models.IntegerField()
    level = models.SmallIntegerField(primary_key=True)
    proficiency_bonus = models.SmallIntegerField()

    class Meta:
        ordering = ["xp"]

    def __str__(self):
        return str(self.level)
