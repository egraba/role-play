# Generated by Django 5.0.1 on 2024-01-14 18:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0011_abilityscore"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="character",
            name="charisma",
        ),
        migrations.RemoveField(
            model_name="character",
            name="charisma_modifier",
        ),
        migrations.RemoveField(
            model_name="character",
            name="constitution",
        ),
        migrations.RemoveField(
            model_name="character",
            name="constitution_modifier",
        ),
        migrations.RemoveField(
            model_name="character",
            name="dexterity",
        ),
        migrations.RemoveField(
            model_name="character",
            name="dexterity_modifier",
        ),
        migrations.RemoveField(
            model_name="character",
            name="intelligence",
        ),
        migrations.RemoveField(
            model_name="character",
            name="intelligence_modifier",
        ),
        migrations.RemoveField(
            model_name="character",
            name="strength",
        ),
        migrations.RemoveField(
            model_name="character",
            name="strength_modifier",
        ),
        migrations.RemoveField(
            model_name="character",
            name="wisdom",
        ),
        migrations.RemoveField(
            model_name="character",
            name="wisdom_modifier",
        ),
        migrations.AddField(
            model_name="character",
            name="ability_scores",
            field=models.ManyToManyField(to="character.abilityscore"),
        ),
    ]
