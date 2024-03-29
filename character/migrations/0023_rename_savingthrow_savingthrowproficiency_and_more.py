# Generated by Django 5.0.2 on 2024-02-14 11:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0022_savingthrow"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="SavingThrow",
            new_name="SavingThrowProficiency",
        ),
        migrations.RemoveField(
            model_name="character",
            name="proficiencies",
        ),
        migrations.AlterModelOptions(
            name="savingthrowproficiency",
            options={"verbose_name_plural": "saving throws proficiencies"},
        ),
        migrations.CreateModel(
            name="ArmorProficiency",
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
                (
                    "armor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.armor",
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
            options={
                "verbose_name_plural": "armor proficiencies",
            },
        ),
        migrations.CreateModel(
            name="SkillsProficiency",
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
                (
                    "character",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.character",
                    ),
                ),
                (
                    "skill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.skill",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "skills proficiencies",
            },
        ),
        migrations.CreateModel(
            name="ToolsProficiency",
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
                (
                    "character",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.character",
                    ),
                ),
                (
                    "tool",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="character.tool"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "tools proficiencies",
            },
        ),
        migrations.CreateModel(
            name="WeaponsProficiency",
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
                (
                    "character",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.character",
                    ),
                ),
                (
                    "weapon",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="character.weapon",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "weapons proficiencies",
            },
        ),
        migrations.DeleteModel(
            name="Proficiencies",
        ),
    ]
