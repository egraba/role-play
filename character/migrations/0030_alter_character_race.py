# Generated by Django 5.0.2 on 2024-03-06 20:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0029_alter_character_gender"),
    ]

    operations = [
        migrations.AlterField(
            model_name="character",
            name="race",
            field=models.CharField(
                choices=[
                    ("human", "Human"),
                    ("halfling", "Halfling"),
                    ("hill_dwarf", "Hill Dwarf"),
                    ("mountain_dwarf", "Mountain Dwarf"),
                    ("high_elf", "High Elf"),
                    ("wood_elf", "Wood Elf"),
                ],
                max_length=14,
            ),
        ),
    ]
