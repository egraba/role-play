# Generated by Django 5.0.1 on 2024-01-19 19:55

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0017_rename_abilityscore_ability_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="ability",
            options={"verbose_name_plural": "abilities"},
        ),
        migrations.RenameField(
            model_name="character",
            old_name="ability_scores",
            new_name="abilities",
        ),
    ]
