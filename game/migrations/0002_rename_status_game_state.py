# Generated by Django 5.0.4 on 2024-04-26 17:21

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="game",
            old_name="status",
            new_name="state",
        ),
    ]