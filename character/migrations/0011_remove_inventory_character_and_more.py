# Generated by Django 4.2.5 on 2023-09-26 17:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0010_rename_proficiency_proficiencies_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="inventory",
            name="character",
        ),
        migrations.RemoveField(
            model_name="proficiencies",
            name="character",
        ),
        migrations.AddField(
            model_name="character",
            name="inventory",
            field=models.OneToOneField(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="character.inventory",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="character",
            name="proficiencies",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="character.proficiencies",
            ),
        ),
    ]