from django.db import models


class Inventory(models.Model):
    capacity = models.SmallIntegerField(default=0)
    gp = models.SmallIntegerField(default=0)


class Equipment(models.Model):
    name = models.CharField(max_length=20)
    inventory = models.ForeignKey(
        Inventory, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.name


class Weapon(models.Model):
    class Name(models.TextChoices):
        CLUB = "Club"
        DAGGER = "Dagger"
        GREATCLUB = "Greatclub"
        HANDAXE = "Handaxe"
        JAVELIN = "Javelin"
        LIGHT_HAMMER = "Light hammer"
        MACE = "Mace"
        QUARTERSTAFF = "Quarterstaff"
        SICKLE = "Sickle"
        SPEAR = "Spear"
        CROSSBOW_LIGHT = "Crossbow, light"
        DART = "Dart"
        SHORTBOW = "Shortbow"
        SLING = "Sling"
        BATTLEAXE = "Battleaxe"
        FLAIL = "Flail"
        GLAIVE = "Glaive"
        GREATAXE = "Greataxe"
        GREATSWORD = "Greatsword"
        HALBERD = "Halberd"
        LANCE = "Lance"
        LONGSWORD = "Longsword"
        MAUL = "Maul"
        MORNINGSTAR = "Morningstar"
        PIKE = "Pike"
        RAPIER = "Rapier"
        SCIMITAR = "Scimitar"
        SHORTSWORD = "Shortsword"
        TRIDENT = "Trident"
        WAR_PICK = "War pick"
        WARHAMMER = "Warhammer"
        WHIP = "Whip"
        BLOWGUN = "Blowgun"
        CROSSBOW_HAND = "Crossbow, hand"
        CROSSBOW_HEAVY = "Crossbow, heavy"
        LONGBOW = "Longbow"
        NET = "Net"

    class Type(models.TextChoices):
        SIMPLE_MELEE = "SM", "Simple Melee"
        SIMPLE_RANGED = "SR", "Simple Ranged"
        MARTIAL_MELEE = "MM", "Martial Melee"
        MARTIAL_RANGED = "MR", "Marial Ranged"

    name = models.CharField(max_length=20, primary_key=True, choices=Name.choices)
    weapon_type = models.CharField(max_length=2, choices=Type.choices)

    def __str__(self):
        return self.name


class Armor(models.Model):
    class Name(models.TextChoices):
        PADDED = "Padded"
        LEATHER = "Leather"
        STUDDED_LEATHER = "Studded leather"
        HIDE = "Hide"
        CHAIN_SHIRT = "Chain shirt"
        SCALE_MAIL = "Scale mail"
        BREASTPLATE = "Breastplate"
        HALF_PLATE = "Half plate"
        RING_MAIL = "Ring mail"
        CHAIN_MAIL = "Chain mail"
        SPLINT = "Splint"
        PLATE = "Plate"
        SHIELD = "Shield"

    class Type(models.TextChoices):
        LIGHT_ARMOR = "LA", "Light Armor"
        MEDIUM_ARMOR = "MA", "Medium Armor"
        HEAVY_ARMOR = "HA", "Heavy Armor"
        SHIELD = "SH", "Shield"

    name = models.CharField(max_length=20, primary_key=True, choices=Name.choices)
    armor_type = models.CharField(max_length=2, choices=Type.choices)

    def __str__(self):
        return self.name


class Pack(models.Model):
    class Name(models.TextChoices):
        BURGLARS_PACK = "Burglar's Pack"
        DIPLOMATS_PACK = "Diplomat's Pack"
        DUNGEONEERS_PACK = "Dungeoneer's Pack"
        ENTERTAINERS_PACK = "Entertainer's Pack"
        EXPLORERS_PACK = "Explorer's Pack"
        PRIESTS_PACK = "Priest's Pack"
        SCHOLARS_PACK = "Scholar's Pack"

    name = models.CharField(max_length=20, primary_key=True, choices=Name.choices)

    def __str__(self):
        return self.name


class Gear(models.Model):
    class Name(models.TextChoices):
        ABACUS = "Abacus"
        ACID = "Acid"
        ALCHEMISTS_FIRE = "Alchemist's fire"
        ARROWS = "Arrows"
        BLOWGUN_NEEDLES = "Blowgun needles"
        CROSSBOW_BOLTS = "Crossbow bolts"
        SLING_BULLETS = "Sling bullets"
        ANTITOXIN = "Antitoxin"
        CRYSTAL = "Crystal"
        ORB = "Orb"
        ROD = "Rod"
        STAFF = "Staff"
        WAND = "Wand"
        BACKPACK = "Backpack"
        BALL_BEARINGS = "Ball bearings"
        BASKET = "Basket"
        BEDROLL = "Bedroll"
        BELL = "Bell"
        BLANKET = "Blanket"
        BLOCK_AND_TACKLE = "Block and tackle"
        BOOK = "Book"
        BOTTLE_GLASS = "Bottle, glass"
        CALTROPS = "Caltrops"
        CANDLE = "Candle"
        CASE_CROSSBOW_BOLT = "Case, crossbow bolt"
        CASE_MAP_OR_SCROLL = "Case, map or scroll"
        CHAIN = "Chain"
        CHALK = "Chalk"
        CHEST = "Chest"
        CLIMBERS_KIT = "Climber's kit"
        CLOTHES_COMMON = "Clothes, common"
        CLOTHES_COSTUME = "Clothes, costume"
        CLOTHES_FINE = "Clothes, fine"
        CLOTHES_TRAVELERS = "Clothes, traveler's"
        COMPONENT_POUCH = "Component pouch"
        CROWBAR = "Crowbar"
        SPRING_OF_MISTLETOE = "Sprig of mistletoe"
        TOTEM = "Totem"
        WOODEN_STAFF = "Wooden staff"
        YEW_WAND = "Yew wand"
        FISHING_TACKLE = "Fishing tackle"
        FLASK_OR_TANKARD = "Flask or tankard"
        GRAPPLING_HOOK = "Grappling hook"
        HAMMER = "Hammer"
        HAMMER_SLEDGE = "Hammer, sledge"
        HEALERS_KIT = "Healer's kit"
        AMULET = "Amulet"
        EMBLEM = "Emblem"
        RELIQUARY = "Reliquary"
        HOLY_WATER = "Holy water"
        HOURGLASS = "Hourglass"
        HUNTING_TRAP = "Hunting trap"
        INK = "Ink"
        INK_PEN = "Ink pen"
        JUG_OR_PITCHER = "Jug or pitcher"
        LADDER = "Ladder"
        LAMP = "Lamp"
        LANTERN_BULLSEYE = "Lantern, bullseye"
        LANTERN_HOODED = "Lantern, hooded"
        LOCK = "Lock"
        MAGNIFYING_GLASS = "Magnifying glass"
        MANACLES = "Manacles"
        MESS_KIT = "Mess kit"
        MIRROR_STEEL = "Mirror, steel"
        OIL = "Oil"
        PAPER = "Paper"
        PARCHMENT = "Parchment"
        PERFUME = "Perfume"
        PICK_MINERS = "Pick, miner's"
        PITON = "Piton"
        POISON_BASIC = "Poison, basic"
        POLE = "Pole"
        POT_IRON = "Pot, iron"
        POTION_OF_HEALING = "Potion of healing"
        POUCH = "Pouch"
        QUIVER = "Quiver"
        RAM_PORTABLE = "Ram, portable"
        RATIONS = "Rations"
        ROBES = "Robes"
        ROPE_HEMPEN = "Rope, hempen"
        ROPE_SILK = "Rope, silk"
        SACK = "Sack"
        SCALE_MERCHANTS = "Scale, merchant's"
        SEALING_WAX = "Sealing wax"
        SHOVEL = "Shovel"
        SIGNAL_WHISTLE = "Signal whistle"
        SIGNET_RING = "Signet ring"
        SOAP = "Soap"
        SPELLBOOK = "Spellbook"
        SPIKES_IRON = "Spikes, iron"
        SPYGLASS = "Spyglass"
        TENT_TWO_PERSONS = "Tent, two-person"
        TINDERBOX = "Tinderbox"
        TORCH = "Torch"
        VIAL = "Vial"
        WATERSKIN = "Waterskin"
        WHETSTONE = "Whetstone"

    class Type(models.TextChoices):
        AMMUNITION = "AM", "Ammunition"
        ARCANE_FOCUS = "AF", "Arcane focus"
        DRUIDIC_FOCUS = "DF", "Druidic focus"
        HOLY_SYMBOL = "HS", "Holy symbol"
        MISC = "MI", "Misc"

    name = models.CharField(max_length=20, primary_key=True, choices=Name.choices)
    gear_type = models.CharField(max_length=2, choices=Type.choices, default=Type.MISC)

    def __str__(self):
        return self.name
