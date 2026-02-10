from django.db.models import TextChoices


class ArmorName(TextChoices):
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


class ArmorType(TextChoices):
    LIGHT_ARMOR = "LA", "Light Armor"
    MEDIUM_ARMOR = "MA", "Medium Armor"
    HEAVY_ARMOR = "HA", "Heavy Armor"
    SHIELD = "SH", "Shield"


class Disadvantage(TextChoices):
    DISADVANTAGE = "D", "disadvantage"


class WeaponProperty(TextChoices):
    AMMUNITION = "ammunition", "Ammunition"
    FINESSE = "finesse", "Finesse"
    HEAVY = "heavy", "Heavy"
    LIGHT = "light", "Light"
    LOADING = "loading", "Loading"
    REACH = "reach", "Reach"
    SPECIAL = "special", "Special"
    THROWN = "thrown", "Thrown"
    TWO_HANDED = "two_handed", "Two-handed"
    VERSATILE = "versatile", "Versatile"


class WeaponMastery(TextChoices):
    """Weapon mastery properties from D&D 5e SRD 5.2.1.

    Each weapon can have one mastery property that provides a special
    effect when used by a character who has mastered that weapon.
    """

    CLEAVE = "cleave", "Cleave"
    # On kill, excess damage carries over to another enemy within 5 feet

    GRAZE = "graze", "Graze"
    # On miss, deal ability modifier damage (minimum 0)

    NICK = "nick", "Nick"
    # Can make extra attack with light weapon as part of Attack action

    PUSH = "push", "Push"
    # On hit, push target 10 feet away (if Large or smaller)

    SAP = "sap", "Sap"
    # On hit, target has disadvantage on next attack before your next turn

    SLOW = "slow", "Slow"
    # On hit, reduce target's speed by 10 feet until start of your next turn

    TOPPLE = "topple", "Topple"
    # On hit, target must make CON save or be knocked prone

    VEX = "vex", "Vex"
    # On hit, gain advantage on next attack against same target before end of turn


class WeaponName(TextChoices):
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


class WeaponType(TextChoices):
    SIMPLE_MELEE = "SM", "Simple Melee"
    SIMPLE_RANGED = "SR", "Simple Ranged"
    MARTIAL_MELEE = "MM", "Martial Melee"
    MARTIAL_RANGED = "MR", "Marial Ranged"


class DamageType(TextChoices):
    BLUDGEONING = "bludgeoning", "bludgeoning"
    PIERCING = "piercing", "piercing"
    SLASHING = "slashing", "slashing"


class PackName(TextChoices):
    BURGLARS_PACK = "Burglar's Pack"
    DIPLOMATS_PACK = "Diplomat's Pack"
    DUNGEONEERS_PACK = "Dungeoneer's Pack"
    ENTERTAINERS_PACK = "Entertainer's Pack"
    EXPLORERS_PACK = "Explorer's Pack"
    PRIESTS_PACK = "Priest's Pack"
    SCHOLARS_PACK = "Scholar's Pack"


class GearName(TextChoices):
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


class GearType(TextChoices):
    AMMUNITION = "AM", "Ammunition"
    ARCANE_FOCUS = "AF", "Arcane focus"
    DRUIDIC_FOCUS = "DF", "Druidic focus"
    HOLY_SYMBOL = "HS", "Holy symbol"
    MISC = "MI", "Misc"


class ToolName(TextChoices):
    ALCHEMISTS_SUPPLIES = "alchemists_supplies", "Alchemist's supplies"
    BREWERS_SUPPLIES = "brewers_supplies", "Brewer's supplies"
    CALLIGRAPHERS_SUPPLIES = "calligraphers_supplies", "Calligrapher's supplies"
    CARPENTERS_TOOLS = "carpenters_tools", "Carpenter's tools"
    CARTOGRAPHERS_TOOLS = "cartographers_tools", "Cartographer's tools"
    COBBLERS_TOOLS = "cobblers_tools", "Cobbler's tools"
    COOKS_UTENSILS = "cooks_utensils", "Cook's utensils"
    GLASSBLOWERS_TOOLS = "glassblowers_tools", "Glassblower's tools"
    JEWELERS_TOOLS = "jewelers_tools", "Jeweler's tools"
    LEATHERWORKERS_TOOLS = "leatherworkers_tools", "Leatherworker's tools"
    MASONS_TOOLS = "masons_tools", "Mason's tools"
    PAINTERS_SUPPLIES = "painters_supplies", "Painter's supplies"
    POTTERS_TOOLS = "potters_tools", "Potter's tools"
    SMITHS_TOOLS = "smiths_tools", "Smith's tools"
    TINKERS_TOOLS = "tinkers_tools", "Tinker's tools"
    WEAVERS_TOOLS = "weavers_tools", "Weaver's tools"
    WOODCARVERS_TOOLS = "woodcarvers_tools", "Woodcarver's tools"
    DISGUISE_KIT = "disguise_kit", "Disguise kit"
    FORGERY_KIT = "forgery_kit", "Forgery kit"
    DICE_SET = "dice_set", "Dice set"
    DRAGONCHESS_SET = "dragonchess_set", "Dragonchess set"
    PLAYING_CARD_SET = "playing_card_set", "Playing card set"
    THREE_DRAGON_ANTE_SET = "three_dragon_ante_set", "Three-Dragon Ante set"
    HERBALISM_KIT = "herbalism_kit", "Herbalism kit"
    BAGPIPES = "bagpipes", "Bagpipes"
    DRUM = "drum", "Drum"
    DULCIMER = "dulcimer", "Dulcimer"
    FLUTE = "flute", "Flute"
    LUTE = "lute", "Lute"
    LYRE = "lyre", "Lyre"
    HORN = "horn", "Horn"
    PAN_FLUTE = "pan_flute", "Pan flute"
    SHAWM = "shawm", "Shawm"
    VIOL = "viol", "Viol"
    NAVIGATORS_TOOLS = "navigators_tools", "Navigator's tools"
    POISONERS_KIT = "poisoners_kit", "Poisoner's kit"
    THIEVES_TOOLS = "thieves_tools", "Thieves' tools"


class ToolType(TextChoices):
    ARTISANS_TOOLS = "AT", "Artisan's tools"
    GAMING_SET = "GS", "Gaming set"
    MUSICAL_INSTRUMENT = "MU", "Musical instrument"
    MISC = "MI", "Misc"
