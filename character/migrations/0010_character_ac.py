# Generated by Django 4.2.4 on 2023-08-27 12:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0009_inventory_equipment"),
    ]

    operations = [
        migrations.AddField(
            model_name="character",
            name="ac",
            field=models.SmallIntegerField(default=0),
        ),
    ]
