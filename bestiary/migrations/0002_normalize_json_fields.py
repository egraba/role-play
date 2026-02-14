"""
Step 1 of 3: Create new relational tables and rename old JSON fields.

The old JSONFields are renamed with a _json suffix so that the new
cached_property methods on MonsterSettings can use the original names.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bestiary", "0001_initial"),
    ]

    operations = [
        # ---- Rename old JSON fields so cached_property names don't collide ----
        migrations.RenameField(
            model_name="monstersettings",
            old_name="speed",
            new_name="speed_json",
        ),
        migrations.RenameField(
            model_name="monstersettings",
            old_name="saving_throws",
            new_name="saving_throws_json",
        ),
        migrations.RenameField(
            model_name="monstersettings",
            old_name="skills",
            new_name="skills_json",
        ),
        migrations.RenameField(
            model_name="monstersettings",
            old_name="senses",
            new_name="senses_json",
        ),
        migrations.RenameField(
            model_name="monstersettings",
            old_name="damage_vulnerabilities",
            new_name="damage_vulnerabilities_json",
        ),
        migrations.RenameField(
            model_name="monstersettings",
            old_name="damage_resistances",
            new_name="damage_resistances_json",
        ),
        migrations.RenameField(
            model_name="monstersettings",
            old_name="damage_immunities",
            new_name="damage_immunities_json",
        ),
        migrations.RenameField(
            model_name="monstersettings",
            old_name="condition_immunities",
            new_name="condition_immunities_json",
        ),
        migrations.RenameField(
            model_name="monstersettings",
            old_name="languages",
            new_name="languages_json",
        ),
        # ---- Add passive_perception field ----
        migrations.AddField(
            model_name="monstersettings",
            name="passive_perception",
            field=models.PositiveSmallIntegerField(
                default=10, help_text="Passive Perception score"
            ),
        ),
        # ---- Create new relational tables ----
        migrations.CreateModel(
            name="MonsterSpeed",
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
                    "movement_type",
                    models.CharField(
                        choices=[
                            ("walk", "Walk"),
                            ("burrow", "Burrow"),
                            ("climb", "Climb"),
                            ("fly", "Fly"),
                            ("swim", "Swim"),
                        ],
                        max_length=10,
                    ),
                ),
                ("feet", models.PositiveSmallIntegerField()),
                (
                    "monster",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="speed_entries",
                        to="bestiary.monstersettings",
                    ),
                ),
            ],
            options={
                "verbose_name": "monster speed",
                "verbose_name_plural": "monster speeds",
                "db_table": "character_monsterspeed",
                "ordering": ["monster", "movement_type"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("monster", "movement_type"),
                        name="unique_monster_speed",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="MonsterSavingThrow",
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
                ("ability", models.CharField(max_length=3)),
                ("bonus", models.SmallIntegerField()),
                (
                    "monster",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="saving_throw_entries",
                        to="bestiary.monstersettings",
                    ),
                ),
            ],
            options={
                "verbose_name": "monster saving throw",
                "verbose_name_plural": "monster saving throws",
                "db_table": "character_monstersavingthrow",
                "ordering": ["monster", "ability"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("monster", "ability"),
                        name="unique_monster_saving_throw",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="MonsterSkill",
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
                ("skill", models.CharField(max_length=30)),
                ("bonus", models.SmallIntegerField()),
                (
                    "monster",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="skill_entries",
                        to="bestiary.monstersettings",
                    ),
                ),
            ],
            options={
                "verbose_name": "monster skill",
                "verbose_name_plural": "monster skills",
                "db_table": "character_monsterskill",
                "ordering": ["monster", "skill"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("monster", "skill"),
                        name="unique_monster_skill",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="MonsterSense",
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
                    "sense_type",
                    models.CharField(
                        choices=[
                            ("blindsight", "Blindsight"),
                            ("darkvision", "Darkvision"),
                            ("tremorsense", "Tremorsense"),
                            ("truesight", "Truesight"),
                        ],
                        max_length=15,
                    ),
                ),
                ("range_feet", models.PositiveSmallIntegerField()),
                (
                    "monster",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sense_entries",
                        to="bestiary.monstersettings",
                    ),
                ),
            ],
            options={
                "verbose_name": "monster sense",
                "verbose_name_plural": "monster senses",
                "db_table": "character_monstersense",
                "ordering": ["monster", "sense_type"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("monster", "sense_type"),
                        name="unique_monster_sense",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="MonsterDamageRelation",
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
                    "damage_type",
                    models.CharField(
                        choices=[
                            ("acid", "Acid"),
                            ("bludgeoning", "Bludgeoning"),
                            ("cold", "Cold"),
                            ("fire", "Fire"),
                            ("force", "Force"),
                            ("lightning", "Lightning"),
                            ("necrotic", "Necrotic"),
                            ("piercing", "Piercing"),
                            ("poison", "Poison"),
                            ("psychic", "Psychic"),
                            ("radiant", "Radiant"),
                            ("slashing", "Slashing"),
                            ("thunder", "Thunder"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "relation_type",
                    models.CharField(
                        choices=[
                            ("vulnerability", "Vulnerability"),
                            ("resistance", "Resistance"),
                            ("immunity", "Immunity"),
                        ],
                        max_length=15,
                    ),
                ),
                (
                    "monster",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="damage_relations",
                        to="bestiary.monstersettings",
                    ),
                ),
            ],
            options={
                "verbose_name": "monster damage relation",
                "verbose_name_plural": "monster damage relations",
                "db_table": "character_monsterdamagerelation",
                "ordering": ["monster", "relation_type", "damage_type"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("monster", "damage_type", "relation_type"),
                        name="unique_monster_damage_relation",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="MonsterConditionImmunity",
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
                ("condition", models.CharField(max_length=20)),
                (
                    "monster",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="condition_immunity_entries",
                        to="bestiary.monstersettings",
                    ),
                ),
            ],
            options={
                "verbose_name": "monster condition immunity",
                "verbose_name_plural": "monster condition immunities",
                "db_table": "character_monsterconditionimmunity",
                "ordering": ["monster", "condition"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("monster", "condition"),
                        name="unique_monster_condition_immunity",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="MonsterLanguage",
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
                ("language", models.CharField(max_length=50)),
                (
                    "monster",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="language_entries",
                        to="bestiary.monstersettings",
                    ),
                ),
            ],
            options={
                "verbose_name": "monster language",
                "verbose_name_plural": "monster languages",
                "db_table": "character_monsterlanguage",
                "ordering": ["monster", "language"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("monster", "language"),
                        name="unique_monster_language",
                    )
                ],
            },
        ),
    ]
