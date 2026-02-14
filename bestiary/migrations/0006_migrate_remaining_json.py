"""
Step 2 of 3 (batch 2): Migrate data from remaining JSON fields
(traits, actions, reactions, legendary_actions, lair_actions, spellcasting)
into their corresponding relational tables.
"""

from django.db import migrations


def forwards(apps, schema_editor):
    MonsterSettings = apps.get_model("bestiary", "MonsterSettings")
    MonsterTrait = apps.get_model("bestiary", "MonsterTrait")
    MonsterActionTemplate = apps.get_model("bestiary", "MonsterActionTemplate")
    MonsterReaction = apps.get_model("bestiary", "MonsterReaction")
    LegendaryActionTemplate = apps.get_model("bestiary", "LegendaryActionTemplate")
    LairActionTemplate = apps.get_model("bestiary", "LairActionTemplate")
    MonsterSpellcasting = apps.get_model("bestiary", "MonsterSpellcasting")
    MonsterSpellcastingLevel = apps.get_model("bestiary", "MonsterSpellcastingLevel")

    for ms in MonsterSettings.objects.all():
        # Traits
        for i, trait in enumerate(ms.traits_json or []):
            MonsterTrait.objects.create(
                monster=ms,
                name=trait["name"],
                description=trait["description"],
                sort_order=i,
            )

        # Actions
        for i, action in enumerate(ms.actions_json or []):
            kwargs = {
                "monster": ms,
                "name": action["name"],
                "description": action["description"],
                "sort_order": i,
            }
            if "attack_bonus" in action:
                kwargs["attack_bonus"] = action["attack_bonus"]
            if "damage_dice" in action:
                kwargs["damage_dice"] = action["damage_dice"]
            MonsterActionTemplate.objects.create(**kwargs)

        # Reactions
        for reaction in ms.reactions_json or []:
            MonsterReaction.objects.create(
                monster=ms,
                name=reaction["name"],
                description=reaction["description"],
                trigger="",
            )

        # Legendary Actions
        for i, la in enumerate(ms.legendary_actions_json or []):
            LegendaryActionTemplate.objects.create(
                monster=ms,
                name=la["name"],
                description=la["description"],
                cost=la.get("cost", 1),
                sort_order=i,
            )

        # Lair Actions
        for i, la in enumerate(ms.lair_actions_json or []):
            LairActionTemplate.objects.create(
                monster=ms,
                description=la["description"],
                sort_order=i,
            )

        # Spellcasting
        sc = ms.spellcasting_json
        if sc and sc.get("ability"):
            entry = MonsterSpellcasting.objects.create(
                monster=ms,
                ability=sc["ability"],
                save_dc=sc["save_dc"],
                attack_bonus=sc["attack_bonus"],
            )
            for key, level_data in (sc.get("spells") or {}).items():
                if key == "cantrips":
                    # Cantrips: flat list of spell names
                    MonsterSpellcastingLevel.objects.create(
                        spellcasting=entry,
                        level="cantrips",
                        slots=0,
                        spells=level_data,
                    )
                else:
                    # Leveled spells: {"slots": N, "spells": [...]}
                    MonsterSpellcastingLevel.objects.create(
                        spellcasting=entry,
                        level=key,
                        slots=level_data["slots"],
                        spells=level_data["spells"],
                    )


def backwards(apps, schema_editor):
    """Reverse: copy relational data back into JSON fields."""
    MonsterSettings = apps.get_model("bestiary", "MonsterSettings")
    MonsterTrait = apps.get_model("bestiary", "MonsterTrait")
    MonsterActionTemplate = apps.get_model("bestiary", "MonsterActionTemplate")
    MonsterReaction = apps.get_model("bestiary", "MonsterReaction")
    LegendaryActionTemplate = apps.get_model("bestiary", "LegendaryActionTemplate")
    LairActionTemplate = apps.get_model("bestiary", "LairActionTemplate")
    MonsterSpellcasting = apps.get_model("bestiary", "MonsterSpellcasting")

    for ms in MonsterSettings.objects.all():
        # Traits
        ms.traits_json = [
            {"name": t.name, "description": t.description}
            for t in MonsterTrait.objects.filter(monster=ms).order_by(
                "sort_order", "name"
            )
        ]

        # Actions
        actions = []
        for a in MonsterActionTemplate.objects.filter(monster=ms).order_by(
            "sort_order", "name"
        ):
            entry = {"name": a.name, "description": a.description}
            if a.attack_bonus is not None:
                entry["attack_bonus"] = a.attack_bonus
            if a.damage_dice:
                entry["damage_dice"] = a.damage_dice
            actions.append(entry)
        ms.actions_json = actions

        # Reactions
        ms.reactions_json = [
            {"name": r.name, "description": r.description}
            for r in MonsterReaction.objects.filter(monster=ms).order_by("name")
        ]

        # Legendary Actions
        ms.legendary_actions_json = [
            {"name": la.name, "description": la.description, "cost": la.cost}
            for la in LegendaryActionTemplate.objects.filter(monster=ms).order_by(
                "sort_order", "cost", "name"
            )
        ]

        # Lair Actions
        ms.lair_actions_json = [
            {"description": la.description}
            for la in LairActionTemplate.objects.filter(monster=ms).order_by(
                "sort_order"
            )
        ]

        # Spellcasting
        try:
            sc = MonsterSpellcasting.objects.get(monster=ms)
        except MonsterSpellcasting.DoesNotExist:
            ms.spellcasting_json = {}
        else:
            spells = {}
            for level in sc.levels.order_by("level"):
                if level.level == "cantrips":
                    spells["cantrips"] = level.spells
                else:
                    spells[level.level] = {
                        "slots": level.slots,
                        "spells": level.spells,
                    }
            ms.spellcasting_json = {
                "ability": sc.ability,
                "save_dc": sc.save_dc,
                "attack_bonus": sc.attack_bonus,
                "spells": spells,
            }

        ms.save()


class Migration(migrations.Migration):
    dependencies = [
        ("bestiary", "0005_rename_json_fields_add_spellcasting"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
