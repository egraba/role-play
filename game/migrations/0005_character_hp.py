# Generated by Django 4.1.3 on 2022-12-04 00:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_game_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='character',
            name='hp',
            field=models.SmallIntegerField(default=100),
        ),
    ]
