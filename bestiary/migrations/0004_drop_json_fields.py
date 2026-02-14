"""
Step 3 of 3: Remove the old renamed JSON fields from MonsterSettings.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("bestiary", "0003_migrate_json_to_relations"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="monstersettings",
            name="speed_json",
        ),
        migrations.RemoveField(
            model_name="monstersettings",
            name="saving_throws_json",
        ),
        migrations.RemoveField(
            model_name="monstersettings",
            name="skills_json",
        ),
        migrations.RemoveField(
            model_name="monstersettings",
            name="senses_json",
        ),
        migrations.RemoveField(
            model_name="monstersettings",
            name="damage_vulnerabilities_json",
        ),
        migrations.RemoveField(
            model_name="monstersettings",
            name="damage_resistances_json",
        ),
        migrations.RemoveField(
            model_name="monstersettings",
            name="damage_immunities_json",
        ),
        migrations.RemoveField(
            model_name="monstersettings",
            name="condition_immunities_json",
        ),
        migrations.RemoveField(
            model_name="monstersettings",
            name="languages_json",
        ),
    ]
