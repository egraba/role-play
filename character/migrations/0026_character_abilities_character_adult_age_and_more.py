# Generated by Django 4.2.5 on 2023-09-08 17:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0025_alter_racialtrait_race"),
    ]

    operations = [
        migrations.AddField(
            model_name="character",
            name="abilities",
            field=models.ManyToManyField(to="character.ability"),
        ),
        migrations.AddField(
            model_name="character",
            name="adult_age",
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="character",
            name="alignment",
            field=models.CharField(
                blank=True,
                choices=[("L", "Lawful"), ("F", "Freedom"), ("N", "None")],
                max_length=1,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="character",
            name="languages",
            field=models.ManyToManyField(to="character.language"),
        ),
        migrations.AddField(
            model_name="character",
            name="life_expectancy",
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="character",
            name="size",
            field=models.CharField(
                blank=True,
                choices=[("S", "Small"), ("M", "Medium")],
                max_length=1,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="character",
            name="speed",
            field=models.SmallIntegerField(blank=True, null=True),
        ),
    ]