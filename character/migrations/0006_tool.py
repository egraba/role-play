# Generated by Django 4.2.6 on 2023-10-13 18:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0005_rename_equipmentpack_pack"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tool",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
        ),
    ]
