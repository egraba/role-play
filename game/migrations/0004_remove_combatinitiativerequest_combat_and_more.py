# Generated by Django 5.0.7 on 2024-08-04 10:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0003_combatinitiativerequest_combatinitiativeresponse_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="combatinitiativerequest",
            name="combat",
        ),
        migrations.AddField(
            model_name="combatinitiativerequest",
            name="fighter",
            field=models.OneToOneField(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="game.fighter",
            ),
            preserve_default=False,
        ),
    ]
