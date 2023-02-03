# Generated by Django 4.1.3 on 2022-12-27 12:01

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Character",
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
                ("name", models.CharField(max_length=255)),
                (
                    "race",
                    models.CharField(
                        choices=[
                            ("H", "Human"),
                            ("O", "Orc"),
                            ("E", "Elf"),
                            ("D", "Dwarf"),
                        ],
                        max_length=1,
                    ),
                ),
                ("xp", models.SmallIntegerField(default=0)),
                ("hp", models.SmallIntegerField(default=100)),
                ("max_hp", models.SmallIntegerField(default=100)),
            ],
        ),
        migrations.CreateModel(
            name="Game",
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
                ("start_date", models.DateTimeField(default=django.utils.timezone.now)),
                ("name", models.CharField(max_length=255)),
                ("end_date", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Narrative",
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
                ("date", models.DateTimeField(default=django.utils.timezone.now)),
                ("message", models.CharField(max_length=1024)),
                (
                    "game",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="game.game",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PendingAction",
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
                    "action_type",
                    models.CharField(
                        choices=[("C", "Make choice"), ("D", "Launch dice")],
                        max_length=1,
                    ),
                ),
                (
                    "character",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="game.character"
                    ),
                ),
                (
                    "game",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="game.game",
                    ),
                ),
                (
                    "narrative",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="game.narrative"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="character",
            name="game",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to="game.game"
            ),
        ),
        migrations.CreateModel(
            name="DiceLaunch",
            fields=[
                (
                    "narrative_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="game.narrative",
                    ),
                ),
                ("score", models.SmallIntegerField()),
                (
                    "character",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="game.character"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("game.narrative",),
        ),
        migrations.CreateModel(
            name="Choice",
            fields=[
                (
                    "narrative_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="game.narrative",
                    ),
                ),
                ("selection", models.CharField(max_length=255)),
                (
                    "character",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="game.character"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("game.narrative",),
        ),
    ]
