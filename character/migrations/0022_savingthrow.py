# Generated by Django 5.0.2 on 2024-02-09 20:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0021_skill_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="SavingThrow",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "ability_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.abilitytype",
                    ),
                ),
                (
                    "character",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.character",
                    ),
                ),
            ],
        ),
    ]
