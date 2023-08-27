# Generated by Django 4.2.4 on 2023-08-26 15:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0006_character_class_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="character",
            name="charisma",
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="character",
            name="constitution",
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="character",
            name="dexterity",
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="character",
            name="intelligence",
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="character",
            name="strength",
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="character",
            name="wisdom",
            field=models.SmallIntegerField(default=0),
        ),
    ]