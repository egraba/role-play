from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Campaign(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    synopsis = models.TextField(
        max_length=3000, help_text="This is the background story of your game."
    )
    main_conflict = models.TextField(
        max_length=1000,
        help_text="""The conflict could be a person, such as a villain, or an event,
        such as a natural disaster or viral disease.
        The conflict will help to provide the objective of the game.""",
    )
    objective = models.TextField(
        max_length=500,
        help_text="""This needs to be clearly outlined in the rules so that all the players
        understand what the main objective of the game is.
        Popular win objectives include reaching a certain number of points,
        achieving an objective, or reaching a certain point in the map.""",
    )

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse("campaign-detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)
