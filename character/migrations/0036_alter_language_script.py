# Generated by Django 5.0.3 on 2024-03-09 06:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0035_language_language_type_language_script_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="language",
            name="script",
            field=models.CharField(
                blank=True,
                choices=[
                    ("common", "Common"),
                    ("dwarvish", "Dwarvish"),
                    ("elvish", "Elvish"),
                    ("giant", "Giant"),
                    ("gnomish", "Gnomish"),
                    ("goblin", "Goblin"),
                    ("halfling", "Halfling"),
                    ("orc", "Orc"),
                    ("abyssal", "Abyssal"),
                    ("celestial", "Celestial"),
                    ("deep_speech", "Deep Speech"),
                    ("draconic", "Draconic"),
                    ("infernal", "Infernal"),
                    ("primordial", "Primordial"),
                    ("sylvan", "Sylvan"),
                    ("undercommon", "Undercommon"),
                ],
                max_length=11,
                null=True,
            ),
        ),
    ]