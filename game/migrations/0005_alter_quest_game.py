# Generated by Django 5.0.8 on 2024-08-14 20:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0004_remove_questupdate_content_questupdate_quest"),
    ]

    operations = [
        migrations.AlterField(
            model_name="quest",
            name="game",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="game.game"
            ),
        ),
    ]