# Generated by Django 4.2.4 on 2023-08-26 12:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0014_rename_tale_quest"),
    ]

    operations = [
        migrations.RenameField(
            model_name="game",
            old_name="story",
            new_name="campaign",
        ),
    ]
