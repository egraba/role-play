# Generated by Django 4.2.6 on 2023-10-11 19:58

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0003_adventuringgear"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="AdventuringGear",
            new_name="Gear",
        ),
    ]
