# Split character app into bestiary, equipment, and magic apps.
# State-only migration: removes models from character's state without touching the DB.

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0023_add_location_field"),
        ("bestiary", "0001_initial"),
        ("equipment", "0001_initial"),
        ("magic", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # Bestiary models
                migrations.DeleteModel(name="LairActionTemplate"),
                migrations.DeleteModel(name="MultiattackAction"),
                migrations.DeleteModel(name="MonsterMultiattack"),
                migrations.DeleteModel(name="LegendaryActionTemplate"),
                migrations.DeleteModel(name="MonsterReaction"),
                migrations.DeleteModel(name="MonsterTrait"),
                migrations.DeleteModel(name="Monster"),
                migrations.DeleteModel(name="MonsterActionTemplate"),
                migrations.DeleteModel(name="MonsterSettings"),
                # Equipment models
                migrations.DeleteModel(name="Armor"),
                migrations.DeleteModel(name="Weapon"),
                migrations.DeleteModel(name="Gear"),
                migrations.DeleteModel(name="Tool"),
                migrations.DeleteModel(name="Pack"),
                migrations.DeleteModel(name="ArmorSettings"),
                migrations.DeleteModel(name="WeaponSettings"),
                migrations.DeleteModel(name="GearSettings"),
                migrations.DeleteModel(name="ToolSettings"),
                migrations.DeleteModel(name="PackSettings"),
                migrations.DeleteModel(name="Attunement"),
                migrations.DeleteModel(name="MagicItem"),
                migrations.DeleteModel(name="MagicItemSettings"),
                migrations.DeleteModel(name="Inventory"),
                # Magic models
                migrations.DeleteModel(name="ActiveSpellEffect"),
                migrations.DeleteModel(name="SummonedCreature"),
                migrations.DeleteModel(name="Concentration"),
                migrations.DeleteModel(name="Spell"),
                migrations.DeleteModel(name="SpellPreparation"),
                migrations.DeleteModel(name="CharacterSpellSlot"),
                migrations.DeleteModel(name="WarlockSpellSlot"),
                migrations.DeleteModel(name="SpellEffectTemplate"),
                migrations.DeleteModel(name="ClassSpellcasting"),
                migrations.DeleteModel(name="SpellSlotTable"),
                migrations.DeleteModel(name="SpellSettings"),
            ],
            database_operations=[],
        ),
    ]
