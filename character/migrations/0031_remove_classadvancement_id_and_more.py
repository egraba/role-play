# Generated by Django 4.2.5 on 2023-09-09 14:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0030_classadvancement"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="classadvancement",
            name="id",
        ),
        migrations.AlterField(
            model_name="classadvancement",
            name="level",
            field=models.SmallIntegerField(primary_key=True, serialize=False),
        ),
    ]
