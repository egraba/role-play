"""
Step 1 of 3 (batch 2): Rename remaining JSON fields with _json suffix
and create MonsterSpellcasting / MonsterSpellcastingLevel tables.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bestiary", "0004_drop_json_fields"),
    ]

    operations = [
        # ── Rename 6 JSON fields ──────────────────────────────────
        migrations.RenameField(
            model_name="monstersettings",
            old_name="traits",
            new_name="traits_json",
        ),
        migrations.RenameField(
            model_name="monstersettings",
            old_name="actions",
            new_name="actions_json",
        ),
        migrations.RenameField(
            model_name="monstersettings",
            old_name="reactions",
            new_name="reactions_json",
        ),
        migrations.RenameField(
            model_name="monstersettings",
            old_name="legendary_actions",
            new_name="legendary_actions_json",
        ),
        migrations.RenameField(
            model_name="monstersettings",
            old_name="lair_actions",
            new_name="lair_actions_json",
        ),
        migrations.RenameField(
            model_name="monstersettings",
            old_name="spellcasting",
            new_name="spellcasting_json",
        ),
        # ── Create MonsterSpellcasting table ──────────────────────
        migrations.CreateModel(
            name="MonsterSpellcasting",
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
                    "ability",
                    models.CharField(
                        help_text="Spellcasting ability abbreviation (INT, WIS, CHA)",
                        max_length=3,
                    ),
                ),
                ("save_dc", models.PositiveSmallIntegerField()),
                ("attack_bonus", models.SmallIntegerField()),
                (
                    "monster",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="spellcasting_entry",
                        to="bestiary.monstersettings",
                    ),
                ),
            ],
            options={
                "verbose_name": "monster spellcasting",
                "verbose_name_plural": "monster spellcasting",
                "db_table": "character_monsterspellcasting",
            },
        ),
        # ── Create MonsterSpellcastingLevel table ─────────────────
        migrations.CreateModel(
            name="MonsterSpellcastingLevel",
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
                    "level",
                    models.CharField(
                        help_text="Spell level: 'cantrips', '1st', '2nd', ... '9th'",
                        max_length=10,
                    ),
                ),
                (
                    "slots",
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text="Number of spell slots (0 for cantrips)",
                    ),
                ),
                (
                    "spells",
                    models.JSONField(
                        default=list,
                        help_text="List of spell name strings",
                    ),
                ),
                (
                    "spellcasting",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="levels",
                        to="bestiary.monsterspellcasting",
                    ),
                ),
            ],
            options={
                "verbose_name": "monster spellcasting level",
                "verbose_name_plural": "monster spellcasting levels",
                "db_table": "character_monsterspellcastinglevel",
                "ordering": ["spellcasting", "level"],
            },
        ),
        migrations.AddConstraint(
            model_name="monsterspellcastinglevel",
            constraint=models.UniqueConstraint(
                fields=("spellcasting", "level"),
                name="unique_monster_spellcasting_level",
            ),
        ),
    ]
