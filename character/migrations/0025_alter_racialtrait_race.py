# Generated by Django 4.2.5 on 2023-09-08 17:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0024_abilityscoreincrease"),
    ]

    operations = [
        migrations.AlterField(
            model_name="racialtrait",
            name="race",
            field=models.CharField(
                choices=[
                    ("H", "Human"),
                    ("G", "Halfling"),
                    ("E", "Elf"),
                    ("D", "Dwarf"),
                ],
                max_length=1,
                unique=True,
            ),
        ),
    ]
