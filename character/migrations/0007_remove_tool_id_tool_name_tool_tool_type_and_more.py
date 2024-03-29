# Generated by Django 4.2.6 on 2023-10-14 15:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("character", "0006_tool"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tool",
            name="id",
        ),
        migrations.AddField(
            model_name="tool",
            name="name",
            field=models.CharField(
                choices=[
                    ("Alchemist's supplies", "Alchemists Supplies"),
                    ("Brewer's supplies", "Brewers Supplies"),
                    ("Calligrapher's supplies", "Calligraphers Supplies"),
                    ("Carpenter's tools", "Carpenters Tools"),
                    ("Cartographer's tools", "Cartographers Tools"),
                    ("Cobbler's tools", "Cobblers Tools"),
                    ("Cook's utensils", "Cooks Utensils"),
                    ("Glassblower's tools", "Glassblowers Tools"),
                    ("Jeweler's tools", "Jewelers Tools"),
                    ("Leatherworker's tools", "Leatherworkers Tools"),
                    ("Mason's tools", "Masons Tools"),
                    ("Painter's supplies", "Painters Supplies"),
                    ("Potter's tools", "Potters Tools"),
                    ("Smith's tools", "Smiths Tools"),
                    ("Tinker's tools", "Tinkers Tools"),
                    ("Weaver's tools", "Weavers Tools"),
                    ("Woodcarver's tools", "Woodcarvers Tools"),
                    ("Disguise kit", "Disguise Kit"),
                    ("Forgery kit", "Forgery Kit"),
                    ("Dice set", "Dice Set"),
                    ("Dragonchess set", "Dragonchess Set"),
                    ("Playing card set", "Playing Card Set"),
                    ("Three-Dragon Ante set", "Three Dragon Ante Set"),
                    ("Herbalism kit", "Herbalism Kit"),
                    ("Bagpipes", "Bagpipes"),
                    ("Drum", "Drum"),
                    ("Dulcimer", "Dulcimer"),
                    ("Flute", "Flute"),
                    ("Lute", "Lute"),
                    ("Lyre", "Lyre"),
                    ("Horn", "Horn"),
                    ("Pan flute", "Pan Flute"),
                    ("Shawm", "Shawm"),
                    ("Viol", "Viol"),
                    ("Navigator's tools", "Navigators Tools"),
                    ("Poisoner's kit", "Poisoners Kit"),
                    ("Thieves' tools", "Thieves Tools"),
                ],
                default=1,
                max_length=30,
                primary_key=True,
                serialize=False,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="tool",
            name="tool_type",
            field=models.CharField(
                choices=[
                    ("AT", "Artisan's tools"),
                    ("GS", "Gaming set"),
                    ("MU", "Musical instrument"),
                    ("MI", "Misc"),
                ],
                default="MI",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="armor",
            name="name",
            field=models.CharField(
                choices=[
                    ("Padded", "Padded"),
                    ("Leather", "Leather"),
                    ("Studded leather", "Studded Leather"),
                    ("Hide", "Hide"),
                    ("Chain shirt", "Chain Shirt"),
                    ("Scale mail", "Scale Mail"),
                    ("Breastplate", "Breastplate"),
                    ("Half plate", "Half Plate"),
                    ("Ring mail", "Ring Mail"),
                    ("Chain mail", "Chain Mail"),
                    ("Splint", "Splint"),
                    ("Plate", "Plate"),
                    ("Shield", "Shield"),
                ],
                max_length=30,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="equipment",
            name="name",
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name="gear",
            name="name",
            field=models.CharField(
                choices=[
                    ("Abacus", "Abacus"),
                    ("Acid", "Acid"),
                    ("Alchemist's fire", "Alchemists Fire"),
                    ("Arrows", "Arrows"),
                    ("Blowgun needles", "Blowgun Needles"),
                    ("Crossbow bolts", "Crossbow Bolts"),
                    ("Sling bullets", "Sling Bullets"),
                    ("Antitoxin", "Antitoxin"),
                    ("Crystal", "Crystal"),
                    ("Orb", "Orb"),
                    ("Rod", "Rod"),
                    ("Staff", "Staff"),
                    ("Wand", "Wand"),
                    ("Backpack", "Backpack"),
                    ("Ball bearings", "Ball Bearings"),
                    ("Basket", "Basket"),
                    ("Bedroll", "Bedroll"),
                    ("Bell", "Bell"),
                    ("Blanket", "Blanket"),
                    ("Block and tackle", "Block And Tackle"),
                    ("Book", "Book"),
                    ("Bottle, glass", "Bottle Glass"),
                    ("Caltrops", "Caltrops"),
                    ("Candle", "Candle"),
                    ("Case, crossbow bolt", "Case Crossbow Bolt"),
                    ("Case, map or scroll", "Case Map Or Scroll"),
                    ("Chain", "Chain"),
                    ("Chalk", "Chalk"),
                    ("Chest", "Chest"),
                    ("Climber's kit", "Climbers Kit"),
                    ("Clothes, common", "Clothes Common"),
                    ("Clothes, costume", "Clothes Costume"),
                    ("Clothes, fine", "Clothes Fine"),
                    ("Clothes, traveler's", "Clothes Travelers"),
                    ("Component pouch", "Component Pouch"),
                    ("Crowbar", "Crowbar"),
                    ("Sprig of mistletoe", "Spring Of Mistletoe"),
                    ("Totem", "Totem"),
                    ("Wooden staff", "Wooden Staff"),
                    ("Yew wand", "Yew Wand"),
                    ("Fishing tackle", "Fishing Tackle"),
                    ("Flask or tankard", "Flask Or Tankard"),
                    ("Grappling hook", "Grappling Hook"),
                    ("Hammer", "Hammer"),
                    ("Hammer, sledge", "Hammer Sledge"),
                    ("Healer's kit", "Healers Kit"),
                    ("Amulet", "Amulet"),
                    ("Emblem", "Emblem"),
                    ("Reliquary", "Reliquary"),
                    ("Holy water", "Holy Water"),
                    ("Hourglass", "Hourglass"),
                    ("Hunting trap", "Hunting Trap"),
                    ("Ink", "Ink"),
                    ("Ink pen", "Ink Pen"),
                    ("Jug or pitcher", "Jug Or Pitcher"),
                    ("Ladder", "Ladder"),
                    ("Lamp", "Lamp"),
                    ("Lantern, bullseye", "Lantern Bullseye"),
                    ("Lantern, hooded", "Lantern Hooded"),
                    ("Lock", "Lock"),
                    ("Magnifying glass", "Magnifying Glass"),
                    ("Manacles", "Manacles"),
                    ("Mess kit", "Mess Kit"),
                    ("Mirror, steel", "Mirror Steel"),
                    ("Oil", "Oil"),
                    ("Paper", "Paper"),
                    ("Parchment", "Parchment"),
                    ("Perfume", "Perfume"),
                    ("Pick, miner's", "Pick Miners"),
                    ("Piton", "Piton"),
                    ("Poison, basic", "Poison Basic"),
                    ("Pole", "Pole"),
                    ("Pot, iron", "Pot Iron"),
                    ("Potion of healing", "Potion Of Healing"),
                    ("Pouch", "Pouch"),
                    ("Quiver", "Quiver"),
                    ("Ram, portable", "Ram Portable"),
                    ("Rations", "Rations"),
                    ("Robes", "Robes"),
                    ("Rope, hempen", "Rope Hempen"),
                    ("Rope, silk", "Rope Silk"),
                    ("Sack", "Sack"),
                    ("Scale, merchant's", "Scale Merchants"),
                    ("Sealing wax", "Sealing Wax"),
                    ("Shovel", "Shovel"),
                    ("Signal whistle", "Signal Whistle"),
                    ("Signet ring", "Signet Ring"),
                    ("Soap", "Soap"),
                    ("Spellbook", "Spellbook"),
                    ("Spikes, iron", "Spikes Iron"),
                    ("Spyglass", "Spyglass"),
                    ("Tent, two-person", "Tent Two Persons"),
                    ("Tinderbox", "Tinderbox"),
                    ("Torch", "Torch"),
                    ("Vial", "Vial"),
                    ("Waterskin", "Waterskin"),
                    ("Whetstone", "Whetstone"),
                ],
                max_length=30,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="pack",
            name="name",
            field=models.CharField(
                choices=[
                    ("Burglar's Pack", "Burglars Pack"),
                    ("Diplomat's Pack", "Diplomats Pack"),
                    ("Dungeoneer's Pack", "Dungeoneers Pack"),
                    ("Entertainer's Pack", "Entertainers Pack"),
                    ("Explorer's Pack", "Explorers Pack"),
                    ("Priest's Pack", "Priests Pack"),
                    ("Scholar's Pack", "Scholars Pack"),
                ],
                max_length=30,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="weapon",
            name="name",
            field=models.CharField(
                choices=[
                    ("Club", "Club"),
                    ("Dagger", "Dagger"),
                    ("Greatclub", "Greatclub"),
                    ("Handaxe", "Handaxe"),
                    ("Javelin", "Javelin"),
                    ("Light hammer", "Light Hammer"),
                    ("Mace", "Mace"),
                    ("Quarterstaff", "Quarterstaff"),
                    ("Sickle", "Sickle"),
                    ("Spear", "Spear"),
                    ("Crossbow, light", "Crossbow Light"),
                    ("Dart", "Dart"),
                    ("Shortbow", "Shortbow"),
                    ("Sling", "Sling"),
                    ("Battleaxe", "Battleaxe"),
                    ("Flail", "Flail"),
                    ("Glaive", "Glaive"),
                    ("Greataxe", "Greataxe"),
                    ("Greatsword", "Greatsword"),
                    ("Halberd", "Halberd"),
                    ("Lance", "Lance"),
                    ("Longsword", "Longsword"),
                    ("Maul", "Maul"),
                    ("Morningstar", "Morningstar"),
                    ("Pike", "Pike"),
                    ("Rapier", "Rapier"),
                    ("Scimitar", "Scimitar"),
                    ("Shortsword", "Shortsword"),
                    ("Trident", "Trident"),
                    ("War pick", "War Pick"),
                    ("Warhammer", "Warhammer"),
                    ("Whip", "Whip"),
                    ("Blowgun", "Blowgun"),
                    ("Crossbow, hand", "Crossbow Hand"),
                    ("Crossbow, heavy", "Crossbow Heavy"),
                    ("Longbow", "Longbow"),
                    ("Net", "Net"),
                ],
                max_length=30,
                primary_key=True,
                serialize=False,
            ),
        ),
    ]
