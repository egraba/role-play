"""
Step 2 of 3: Migrate data from renamed JSON fields to new relational tables.
"""

from django.db import migrations

# Valid SenseType values (must match the SenseType enum)
VALID_SENSES = {"blindsight", "darkvision", "tremorsense", "truesight"}


def forwards(apps, schema_editor):
    MonsterSettings = apps.get_model("bestiary", "MonsterSettings")
    MonsterSpeed = apps.get_model("bestiary", "MonsterSpeed")
    MonsterSavingThrow = apps.get_model("bestiary", "MonsterSavingThrow")
    MonsterSkill = apps.get_model("bestiary", "MonsterSkill")
    MonsterSense = apps.get_model("bestiary", "MonsterSense")
    MonsterDamageRelation = apps.get_model("bestiary", "MonsterDamageRelation")
    MonsterConditionImmunity = apps.get_model("bestiary", "MonsterConditionImmunity")
    MonsterLanguage = apps.get_model("bestiary", "MonsterLanguage")

    for ms in MonsterSettings.objects.all():
        # Speed
        speed_data = ms.speed_json or {}
        for movement_type, feet in speed_data.items():
            MonsterSpeed.objects.create(
                monster=ms, movement_type=movement_type, feet=feet
            )

        # Saving throws
        saves_data = ms.saving_throws_json or {}
        for ability, bonus in saves_data.items():
            MonsterSavingThrow.objects.create(monster=ms, ability=ability, bonus=bonus)

        # Skills — normalize keys to Title Case for SkillName compat
        skills_data = ms.skills_json or {}
        for skill, bonus in skills_data.items():
            MonsterSkill.objects.create(monster=ms, skill=skill.title(), bonus=bonus)

        # Senses — separate passive_perception into dedicated field
        senses_data = ms.senses_json or {}
        for sense_key, value in senses_data.items():
            if sense_key == "passive_perception":
                ms.passive_perception = value
            elif sense_key in VALID_SENSES:
                MonsterSense.objects.create(
                    monster=ms, sense_type=sense_key, range_feet=value
                )
        ms.save(update_fields=["passive_perception"])

        # Damage vulnerabilities
        for dt in ms.damage_vulnerabilities_json or []:
            MonsterDamageRelation.objects.create(
                monster=ms, damage_type=dt, relation_type="vulnerability"
            )

        # Damage resistances
        for dt in ms.damage_resistances_json or []:
            MonsterDamageRelation.objects.create(
                monster=ms, damage_type=dt, relation_type="resistance"
            )

        # Damage immunities
        for dt in ms.damage_immunities_json or []:
            MonsterDamageRelation.objects.create(
                monster=ms, damage_type=dt, relation_type="immunity"
            )

        # Condition immunities
        for cond in ms.condition_immunities_json or []:
            MonsterConditionImmunity.objects.create(monster=ms, condition=cond)

        # Languages
        for lang in ms.languages_json or []:
            MonsterLanguage.objects.create(monster=ms, language=lang)


def backwards(apps, schema_editor):
    """Reverse: copy relational data back into JSON fields."""
    MonsterSettings = apps.get_model("bestiary", "MonsterSettings")
    MonsterSpeed = apps.get_model("bestiary", "MonsterSpeed")
    MonsterSavingThrow = apps.get_model("bestiary", "MonsterSavingThrow")
    MonsterSkill = apps.get_model("bestiary", "MonsterSkill")
    MonsterSense = apps.get_model("bestiary", "MonsterSense")
    MonsterDamageRelation = apps.get_model("bestiary", "MonsterDamageRelation")
    MonsterConditionImmunity = apps.get_model("bestiary", "MonsterConditionImmunity")
    MonsterLanguage = apps.get_model("bestiary", "MonsterLanguage")

    for ms in MonsterSettings.objects.all():
        ms.speed_json = {
            e.movement_type: e.feet for e in MonsterSpeed.objects.filter(monster=ms)
        }
        ms.saving_throws_json = {
            e.ability: e.bonus for e in MonsterSavingThrow.objects.filter(monster=ms)
        }
        ms.skills_json = {
            e.skill.lower(): e.bonus for e in MonsterSkill.objects.filter(monster=ms)
        }

        senses = {
            e.sense_type: e.range_feet for e in MonsterSense.objects.filter(monster=ms)
        }
        senses["passive_perception"] = ms.passive_perception
        ms.senses_json = senses

        ms.damage_vulnerabilities_json = list(
            MonsterDamageRelation.objects.filter(
                monster=ms, relation_type="vulnerability"
            ).values_list("damage_type", flat=True)
        )
        ms.damage_resistances_json = list(
            MonsterDamageRelation.objects.filter(
                monster=ms, relation_type="resistance"
            ).values_list("damage_type", flat=True)
        )
        ms.damage_immunities_json = list(
            MonsterDamageRelation.objects.filter(
                monster=ms, relation_type="immunity"
            ).values_list("damage_type", flat=True)
        )
        ms.condition_immunities_json = list(
            MonsterConditionImmunity.objects.filter(monster=ms).values_list(
                "condition", flat=True
            )
        )
        ms.languages_json = list(
            MonsterLanguage.objects.filter(monster=ms).values_list(
                "language", flat=True
            )
        )
        ms.save()


class Migration(migrations.Migration):
    dependencies = [
        ("bestiary", "0002_normalize_json_fields"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
