# Generated by Django 4.2.2 on 2023-07-01 19:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0003_game_master_delete_master"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="name",
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
