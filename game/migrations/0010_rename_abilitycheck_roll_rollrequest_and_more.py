# Generated by Django 5.0.2 on 2024-02-09 21:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0022_savingthrow"),
        ("game", "0009_alter_abilitycheck_result"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="AbilityCheck",
            new_name="Roll",
        ),
        migrations.CreateModel(
            name="RollRequest",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="game.event",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("P", "Pending"), ("D", "Done")],
                        default="P",
                        max_length=1,
                    ),
                ),
                (
                    "difficulty_class",
                    models.SmallIntegerField(
                        choices=[
                            (5, "Very easy"),
                            (10, "Easy"),
                            (15, "Medium"),
                            (20, "Hard"),
                            (25, "Very hard"),
                            (30, "Nearly impossible"),
                        ]
                    ),
                ),
                (
                    "roll_type",
                    models.SmallIntegerField(
                        choices=[
                            (1, "Ability check"),
                            (2, "Saving throw"),
                            (3, "Attack"),
                        ]
                    ),
                ),
                (
                    "ability_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.abilitytype",
                    ),
                ),
                (
                    "character",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.character",
                    ),
                ),
            ],
            bases=("game.event",),
        ),
        migrations.AlterField(
            model_name="roll",
            name="request",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="game.rollrequest"
            ),
        ),
        migrations.DeleteModel(
            name="AbilityCheckRequest",
        ),
    ]
