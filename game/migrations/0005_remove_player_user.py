# Generated by Django 4.2.3 on 2023-07-27 20:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0004_alter_player_game_alter_player_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="player",
            name="user",
        ),
    ]
