# Generated by Django 5.0.7 on 2024-07-15 08:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0009_alter_fighter_character"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fighter",
            name="combat",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="game.combat",
            ),
        ),
    ]
