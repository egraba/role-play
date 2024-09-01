# Generated by Django 5.1 on 2024-09-01 14:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="character",
            name="creation_state",
            field=models.SmallIntegerField(
                choices=[(1, "base_attributes_selection"), (0, "complete")], default=1
            ),
        ),
    ]