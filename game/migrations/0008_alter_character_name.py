# Generated by Django 4.1.7 on 2023-03-03 17:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0007_alter_character_game_alter_character_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="character",
            name="name",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
