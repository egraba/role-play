# Generated by Django 5.0.7 on 2024-07-14 15:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0007_fighter_dexterity_check"),
    ]

    operations = [
        migrations.AddField(
            model_name="rollrequest",
            name="is_combat",
            field=models.BooleanField(default=False),
        ),
    ]