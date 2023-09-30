# Generated by Django 4.2.5 on 2023-09-26 18:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0012_alter_character_inventory"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="classfeature",
            name="hit_dice",
        ),
        migrations.RemoveField(
            model_name="classfeature",
            name="hp_first_level",
        ),
        migrations.RemoveField(
            model_name="classfeature",
            name="hp_higher_levels",
        ),
        migrations.CreateModel(
            name="HitPoints",
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
                ("hit_dice", models.CharField(max_length=5)),
                ("hp_first_level", models.SmallIntegerField()),
                ("hp_higher_levels", models.SmallIntegerField()),
                (
                    "class_feature",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="character.classfeature",
                    ),
                ),
            ],
        ),
    ]
