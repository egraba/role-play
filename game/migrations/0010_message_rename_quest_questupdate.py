# Generated by Django 5.0.7 on 2024-07-28 16:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0009_remove_event_message"),
    ]

    operations = [
        migrations.CreateModel(
            name="Message",
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
                ("content", models.CharField(max_length=100)),
            ],
            bases=("game.event",),
        ),
        migrations.RenameModel(
            old_name="Quest",
            new_name="QuestUpdate",
        ),
    ]
