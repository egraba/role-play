from django.db import models


class DexterityCheckDisadvantage(models.Model):
    character = models.ForeignKey("character.Character", on_delete=models.CASCADE)
