# Generated by Django 5.0.2 on 2024-03-03 09:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0028_alter_klassadvancement_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="character",
            name="gender",
            field=models.CharField(
                choices=[("M", "Male"), ("F", "Female"), ("A", "Androgynous")],
                default="M",
                max_length=1,
            ),
        ),
    ]
