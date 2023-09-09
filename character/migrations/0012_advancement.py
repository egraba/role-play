# Generated by Django 4.2.4 on 2023-08-27 13:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0011_weapon_delete_equipment"),
    ]

    operations = [
        migrations.CreateModel(
            name="Advancement",
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
                ("xp", models.SmallIntegerField()),
                ("level", models.SmallIntegerField(unique=True)),
                ("proficiency_bonus", models.SmallIntegerField()),
            ],
        ),
    ]
