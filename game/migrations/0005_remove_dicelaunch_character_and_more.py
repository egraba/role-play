# Generated by Django 5.0.1 on 2024-02-02 07:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0004_delete_choice"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="dicelaunch",
            name="character",
        ),
        migrations.RemoveField(
            model_name="dicelaunch",
            name="event_ptr",
        ),
        migrations.RemoveField(
            model_name="healing",
            name="character",
        ),
        migrations.RemoveField(
            model_name="healing",
            name="event_ptr",
        ),
        migrations.RemoveField(
            model_name="xpincrease",
            name="character",
        ),
        migrations.RemoveField(
            model_name="xpincrease",
            name="event_ptr",
        ),
        migrations.DeleteModel(
            name="Damage",
        ),
        migrations.DeleteModel(
            name="DiceLaunch",
        ),
        migrations.DeleteModel(
            name="Healing",
        ),
        migrations.DeleteModel(
            name="XpIncrease",
        ),
    ]
