# Generated by Django 4.2.3 on 2023-07-07 20:13

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("master", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="story",
            old_name="synopis",
            new_name="synopsis",
        ),
    ]
