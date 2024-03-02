# Generated by Django 5.0.2 on 2024-02-13 09:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0010_rename_abilitycheck_roll_rollrequest_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="rollrequest",
            name="against",
            field=models.CharField(
                blank=True,
                choices=[("F", "Being frightened"), ("C", "Charm"), ("P", "Poison")],
                max_length=1,
                null=True,
            ),
        ),
    ]
