from django.db import models

class Master(models.Model):
    name = models.CharField(max_length=255)