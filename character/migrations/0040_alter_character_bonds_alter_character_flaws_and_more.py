# Generated by Django 5.0.3 on 2024-03-16 07:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0039_merge_20240315_0349"),
    ]

    operations = [
        migrations.AlterField(
            model_name="character",
            name="bonds",
            field=models.TextField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name="character",
            name="flaws",
            field=models.TextField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name="character",
            name="ideals",
            field=models.TextField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name="character",
            name="personality_traits",
            field=models.TextField(max_length=150),
        ),
    ]
