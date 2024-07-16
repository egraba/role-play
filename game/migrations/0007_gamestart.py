# Generated by Django 5.0.7 on 2024-07-16 14:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0006_remove_event_event_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="GameStart",
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
            ],
            bases=("game.event",),
        ),
    ]
