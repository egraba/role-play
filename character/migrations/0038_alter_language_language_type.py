# Generated by Django 5.0.3 on 2024-03-14 21:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0037_character_bonds_character_flaws_character_ideals_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="language",
            name="language_type",
            field=models.CharField(
                choices=[("S", "Standard"), ("E", "Exotic")], max_length=1
            ),
        ),
    ]