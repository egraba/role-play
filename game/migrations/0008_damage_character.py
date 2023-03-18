# Generated by Django 4.1.7 on 2023-03-18 08:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0007_xpincrease_character"),
    ]

    operations = [
        migrations.AddField(
            model_name="damage",
            name="character",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="game.character",
            ),
            preserve_default=False,
        ),
    ]
