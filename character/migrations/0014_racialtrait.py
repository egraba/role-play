# Generated by Django 4.2.4 on 2023-09-03 17:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0013_alter_advancement_xp_alter_character_xp"),
    ]

    operations = [
        migrations.CreateModel(
            name="RacialTrait",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "race",
                    models.CharField(
                        choices=[
                            ("H", "Human"),
                            ("G", "Halfling"),
                            ("E", "Elf"),
                            ("D", "Dwarf"),
                        ],
                        max_length=1,
                    ),
                ),
                ("adult_age", models.SmallIntegerField()),
                ("life_expectancy", models.SmallIntegerField()),
                (
                    "alignment",
                    models.CharField(
                        choices=[("L", "Lawful"), ("F", "Freedom"), ("N", "None")],
                        max_length=1,
                    ),
                ),
                ("size", models.SmallIntegerField()),
                ("speed", models.SmallIntegerField()),
            ],
        ),
    ]
