from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Story(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    synopsis = models.TextField(max_length=3000)
    main_conflict = models.TextField(max_length=1000)
    objective = models.TextField(max_length=500)

    class Meta:
        verbose_name_plural = "stories"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("story-detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)
