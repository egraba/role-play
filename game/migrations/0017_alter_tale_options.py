# Generated by Django 4.2 on 2023-04-12 19:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0016_alter_event_options_event_game_event_date_707313_idx"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tale",
            options={"ordering": ["-date"]},
        ),
    ]
