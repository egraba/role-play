# Generated by Django 4.2.3 on 2023-07-18 09:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0003_remove_game_master_master"),
        ("master", "0009_master"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Master",
        ),
    ]