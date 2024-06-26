# Generated by Django 5.0.4 on 2024-04-19 18:07

import django.db.models.deletion
import django.db.models.functions.text
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("character", "0041_rename_bonds_character_bond_and_more"),
        ("master", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
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
                ("date", models.DateTimeField(auto_now_add=True)),
                ("message", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Quest",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="game.event",
                    ),
                ),
                ("content", models.CharField(max_length=1000)),
            ],
            bases=("game.event",),
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
                ("name", models.CharField(max_length=100)),
                ("start_date", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("P", "Under preparation"), ("O", "Ongoing")],
                        default="P",
                        max_length=1,
                    ),
                ),
                (
                    "campaign",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="master.campaign",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="event",
            name="game",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="game.game"
            ),
        ),
        migrations.CreateModel(
            name="Master",
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
                    "game",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="game.game"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Player",
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
                    "character",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.character",
                    ),
                ),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="game.game"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RollRequest",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="game.event",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("P", "Pending"), ("D", "Done")],
                        default="P",
                        max_length=1,
                    ),
                ),
                (
                    "ability_type",
                    models.CharField(
                        choices=[
                            ("STR", "Strength"),
                            ("DEX", "Dexterity"),
                            ("CON", "Constitution"),
                            ("INT", "Intelligence"),
                            ("WIS", "Wisdom"),
                            ("CHA", "Charisma"),
                        ],
                        max_length=3,
                    ),
                ),
                (
                    "difficulty_class",
                    models.SmallIntegerField(
                        choices=[
                            (5, "Very easy"),
                            (10, "Easy"),
                            (15, "Medium"),
                            (20, "Hard"),
                            (25, "Very hard"),
                            (30, "Nearly impossible"),
                        ]
                    ),
                ),
                (
                    "roll_type",
                    models.SmallIntegerField(
                        choices=[
                            (1, "Ability check"),
                            (2, "Saving throw"),
                            (3, "Attack"),
                        ]
                    ),
                ),
                (
                    "against",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("F", "Being frightened"),
                            ("C", "Charm"),
                            ("P", "Poison"),
                        ],
                        max_length=1,
                        null=True,
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
            bases=("game.event",),
        ),
        migrations.CreateModel(
            name="Roll",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="game.event",
                    ),
                ),
                (
                    "result",
                    models.CharField(
                        choices=[("S", "Success"), ("F", "Failure")], max_length=1
                    ),
                ),
                (
                    "character",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.character",
                    ),
                ),
                (
                    "request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="game.rollrequest",
                    ),
                ),
            ],
            bases=("game.event",),
        ),
        migrations.AddIndex(
            model_name="game",
            index=models.Index(
                django.db.models.functions.text.Upper("name"),
                name="game_name_upper_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="event",
            index=models.Index(fields=["-date"], name="game_event_date_707313_idx"),
        ),
    ]
