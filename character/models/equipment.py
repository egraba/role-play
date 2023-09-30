from django.db import models


class Inventory(models.Model):
    capacity = models.SmallIntegerField(default=0)
    gp = models.SmallIntegerField(default=0)


class Equipment(models.Model):
    name = models.CharField(max_length=20)
    inventory = models.ForeignKey(
        Inventory, on_delete=models.SET_NULL, null=True, blank=True
    )
    weight = models.SmallIntegerField()

    def __str__(self):
        return self.name
