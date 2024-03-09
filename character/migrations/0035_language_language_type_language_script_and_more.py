# Generated by Django 5.0.3 on 2024-03-09 05:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0034_alter_language_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="language",
            name="language_type",
            field=models.CharField(
                choices=[("S", "Standard"), ("E", "EXOTIC")], default=1, max_length=1
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="language",
            name="script",
            field=models.CharField(
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
                default=1,
                max_length=11,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="language",
            name="name",
            field=models.CharField(
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
                unique=True,
            ),
        ),
    ]
