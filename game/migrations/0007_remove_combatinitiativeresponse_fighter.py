# Generated by Django 5.0.7 on 2024-08-04 18:08

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0006_remove_combatinitiativeresponse_combat_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="combatinitiativeresponse",
            name="fighter",
        ),
    ]
