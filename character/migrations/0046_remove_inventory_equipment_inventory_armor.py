# Generated by Django 5.0.3 on 2024-04-12 11:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0045_remove_equipment_name_armor_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="inventory",
            name="equipment",
        ),
        migrations.AddField(
            model_name="inventory",
            name="armor",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="character.armor",
            ),
        ),
    ]
