# Generated by Django 4.2.5 on 2023-09-26 17:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0011_remove_inventory_character_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="character",
            name="inventory",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="character.inventory",
            ),
        ),
    ]
