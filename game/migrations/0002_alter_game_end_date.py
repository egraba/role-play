# Generated by Django 4.1.3 on 2022-12-03 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
