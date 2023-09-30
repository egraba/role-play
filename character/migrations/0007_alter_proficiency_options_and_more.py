# Generated by Django 4.2.5 on 2023-09-22 20:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0006_character_hp_increase"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="proficiency",
            options={"verbose_name_plural": "proficiencies"},
        ),
        migrations.RemoveField(
            model_name="classfeature",
            name="proficiencies",
        ),
        migrations.AddField(
            model_name="proficiency",
            name="class_feature",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="character.classfeature",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="proficiency",
            name="armor",
            field=models.TextField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="proficiency",
            name="saving_throws",
            field=models.TextField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="proficiency",
            name="skills",
            field=models.TextField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="proficiency",
            name="tools",
            field=models.TextField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="proficiency",
            name="weapons",
            field=models.TextField(blank=True, max_length=50, null=True),
        ),
    ]