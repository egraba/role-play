# Generated by Django 4.2.3 on 2023-07-09 13:01

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("master", "0006_alter_story_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="story",
            name="objective",
            field=models.TextField(default=django.utils.timezone.now, max_length=500),
            preserve_default=False,
        ),
    ]
