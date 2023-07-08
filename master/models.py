from django.db import models


class Story(models.Model):
    name = models.CharField(max_length=50, unique=True)
    synopsis = models.CharField(max_length=3000)
    main_conflict = models.CharField(max_length=1000)

    def __str__(self):
        return self.name
