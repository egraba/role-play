# Generated by Django 5.0.7 on 2024-07-14 15:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0066_alter_weaponsettings_damage_and_more"),
        ("game", "0008_rollrequest_is_combat"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fighter",
            name="character",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="character.character"
            ),
        ),
    ]