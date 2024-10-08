# Generated by Django 5.0.8 on 2024-08-16 15:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0005_alter_quest_game"),
    ]

    operations = [
        migrations.CreateModel(
            name="CombatInitativeOrderSet",
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
                    "combat",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="game.combat"
                    ),
                ),
            ],
            bases=("game.event",),
        ),
    ]
