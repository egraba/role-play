from django.db import models


class Story(models.Model):
    title = models.CharField(max_length=50, unique=True)
    synopsis = models.TextField(max_length=3000)
    main_conflict = models.TextField(max_length=1000)

    def __str__(self):
        return self.title
