# Generated by Django 4.2.5 on 2023-09-22 21:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0007_alter_proficiency_options_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="proficiency",
            name="class_feature",
        ),
        migrations.AddField(
            model_name="character",
            name="proficiencies",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="character.proficiency",
            ),
        ),
        migrations.AddField(
            model_name="classfeature",
            name="proficiencies",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="character.proficiency",
            ),
        ),
    ]