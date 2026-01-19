"""
Monster constants for D&D 5e SRD.

This module defines enums for monster stat blocks including:
- Size categories
- Creature types
- Alignments
- Challenge ratings
- Senses
"""

from django.db.models import TextChoices


class CreatureSize(TextChoices):
    """Creature size categories per D&D 5e SRD."""

    TINY = "tiny", "Tiny"
    SMALL = "small", "Small"
    MEDIUM = "medium", "Medium"
    LARGE = "large", "Large"
    HUGE = "huge", "Huge"
    GARGANTUAN = "gargantuan", "Gargantuan"


class CreatureType(TextChoices):
    """Creature types per D&D 5e SRD."""

    ABERRATION = "aberration", "Aberration"
    BEAST = "beast", "Beast"
    CELESTIAL = "celestial", "Celestial"
    CONSTRUCT = "construct", "Construct"
    DRAGON = "dragon", "Dragon"
    ELEMENTAL = "elemental", "Elemental"
    FEY = "fey", "Fey"
    FIEND = "fiend", "Fiend"
    GIANT = "giant", "Giant"
    HUMANOID = "humanoid", "Humanoid"
    MONSTROSITY = "monstrosity", "Monstrosity"
    OOZE = "ooze", "Ooze"
    PLANT = "plant", "Plant"
    UNDEAD = "undead", "Undead"


class Alignment(TextChoices):
    """Alignment options per D&D 5e SRD."""

    LAWFUL_GOOD = "LG", "Lawful Good"
    NEUTRAL_GOOD = "NG", "Neutral Good"
    CHAOTIC_GOOD = "CG", "Chaotic Good"
    LAWFUL_NEUTRAL = "LN", "Lawful Neutral"
    TRUE_NEUTRAL = "N", "Neutral"
    CHAOTIC_NEUTRAL = "CN", "Chaotic Neutral"
    LAWFUL_EVIL = "LE", "Lawful Evil"
    NEUTRAL_EVIL = "NE", "Neutral Evil"
    CHAOTIC_EVIL = "CE", "Chaotic Evil"
    UNALIGNED = "U", "Unaligned"
    ANY = "any", "Any Alignment"


class ChallengeRating(TextChoices):
    """
    Challenge ratings per D&D 5e SRD.

    CR determines monster difficulty and XP reward.
    """

    CR_0 = "0", "0"
    CR_1_8 = "1/8", "1/8"
    CR_1_4 = "1/4", "1/4"
    CR_1_2 = "1/2", "1/2"
    CR_1 = "1", "1"
    CR_2 = "2", "2"
    CR_3 = "3", "3"
    CR_4 = "4", "4"
    CR_5 = "5", "5"
    CR_6 = "6", "6"
    CR_7 = "7", "7"
    CR_8 = "8", "8"
    CR_9 = "9", "9"
    CR_10 = "10", "10"
    CR_11 = "11", "11"
    CR_12 = "12", "12"
    CR_13 = "13", "13"
    CR_14 = "14", "14"
    CR_15 = "15", "15"
    CR_16 = "16", "16"
    CR_17 = "17", "17"
    CR_18 = "18", "18"
    CR_19 = "19", "19"
    CR_20 = "20", "20"
    CR_21 = "21", "21"
    CR_22 = "22", "22"
    CR_23 = "23", "23"
    CR_24 = "24", "24"
    CR_25 = "25", "25"
    CR_26 = "26", "26"
    CR_27 = "27", "27"
    CR_28 = "28", "28"
    CR_29 = "29", "29"
    CR_30 = "30", "30"


# XP by Challenge Rating per D&D 5e SRD
CR_XP_TABLE = {
    "0": 0,
    "1/8": 25,
    "1/4": 50,
    "1/2": 100,
    "1": 200,
    "2": 450,
    "3": 700,
    "4": 1100,
    "5": 1800,
    "6": 2300,
    "7": 2900,
    "8": 3900,
    "9": 5000,
    "10": 5900,
    "11": 7200,
    "12": 8400,
    "13": 10000,
    "14": 11500,
    "15": 13000,
    "16": 15000,
    "17": 18000,
    "18": 20000,
    "19": 22000,
    "20": 25000,
    "21": 33000,
    "22": 41000,
    "23": 50000,
    "24": 62000,
    "25": 75000,
    "26": 90000,
    "27": 105000,
    "28": 120000,
    "29": 135000,
    "30": 155000,
}


class DamageType(TextChoices):
    """
    All damage types per D&D 5e SRD.

    Used for resistances, immunities, and vulnerabilities.
    """

    ACID = "acid", "Acid"
    BLUDGEONING = "bludgeoning", "Bludgeoning"
    COLD = "cold", "Cold"
    FIRE = "fire", "Fire"
    FORCE = "force", "Force"
    LIGHTNING = "lightning", "Lightning"
    NECROTIC = "necrotic", "Necrotic"
    PIERCING = "piercing", "Piercing"
    POISON = "poison", "Poison"
    PSYCHIC = "psychic", "Psychic"
    RADIANT = "radiant", "Radiant"
    SLASHING = "slashing", "Slashing"
    THUNDER = "thunder", "Thunder"


class ActionType(TextChoices):
    """Types of monster actions per D&D 5e SRD."""

    # Standard actions
    MELEE_WEAPON = "melee_weapon", "Melee Weapon Attack"
    RANGED_WEAPON = "ranged_weapon", "Ranged Weapon Attack"
    MELEE_SPELL = "melee_spell", "Melee Spell Attack"
    RANGED_SPELL = "ranged_spell", "Ranged Spell Attack"
    MULTIATTACK = "multiattack", "Multiattack"
    SPECIAL = "special", "Special Ability"

    # Legendary and Lair
    LEGENDARY = "legendary", "Legendary Action"
    LAIR = "lair", "Lair Action"

    # Reactions
    REACTION = "reaction", "Reaction"


class RechargeType(TextChoices):
    """Recharge conditions for monster abilities."""

    NONE = "none", "No Recharge"
    RECHARGE_5_6 = "5-6", "Recharge 5-6"
    RECHARGE_6 = "6", "Recharge 6"
    RECHARGE_4_6 = "4-6", "Recharge 4-6"
    SHORT_REST = "short_rest", "Recharges on Short Rest"
    LONG_REST = "long_rest", "Recharges on Long Rest"
    DAILY_1 = "daily_1", "1/Day"
    DAILY_2 = "daily_2", "2/Day"
    DAILY_3 = "daily_3", "3/Day"


class SaveType(TextChoices):
    """Saving throw types for monster abilities."""

    NONE = "none", "None"
    STRENGTH = "STR", "Strength"
    DEXTERITY = "DEX", "Dexterity"
    CONSTITUTION = "CON", "Constitution"
    INTELLIGENCE = "INT", "Intelligence"
    WISDOM = "WIS", "Wisdom"
    CHARISMA = "CHA", "Charisma"


class SaveEffect(TextChoices):
    """Effect on successful save."""

    NONE = "none", "None"
    HALF_DAMAGE = "half_damage", "Half Damage"
    NEGATES = "negates", "Negates Effect"
    ENDS_EFFECT = "ends_effect", "Ends Effect"


class AreaShape(TextChoices):
    """Area of effect shapes."""

    NONE = "none", "None"
    SPHERE = "sphere", "Sphere"
    CUBE = "cube", "Cube"
    CONE = "cone", "Cone"
    LINE = "line", "Line"
    CYLINDER = "cylinder", "Cylinder"


class SenseType(TextChoices):
    """Special senses per D&D 5e SRD."""

    BLINDSIGHT = "blindsight", "Blindsight"
    DARKVISION = "darkvision", "Darkvision"
    TREMORSENSE = "tremorsense", "Tremorsense"
    TRUESIGHT = "truesight", "Truesight"


class MovementType(TextChoices):
    """Movement types per D&D 5e SRD."""

    WALK = "walk", "Walk"
    BURROW = "burrow", "Burrow"
    CLIMB = "climb", "Climb"
    FLY = "fly", "Fly"
    SWIM = "swim", "Swim"


class MonsterName(TextChoices):
    """
    Monster names from D&D 5e SRD.

    Organized by creature type for easier reference.
    """

    # Aberrations
    ABOLETH = "Aboleth"

    # Beasts
    APE = "Ape"
    BAT = "Bat"
    BLACK_BEAR = "Black Bear"
    BOAR = "Boar"
    BROWN_BEAR = "Brown Bear"
    CAT = "Cat"
    CONSTRICTOR_SNAKE = "Constrictor Snake"
    CROCODILE = "Crocodile"
    DIRE_WOLF = "Dire Wolf"
    FROG = "Frog"
    GIANT_APE = "Giant Ape"
    GIANT_BAT = "Giant Bat"
    GIANT_BOAR = "Giant Boar"
    GIANT_CONSTRICTOR_SNAKE = "Giant Constrictor Snake"
    GIANT_CROCODILE = "Giant Crocodile"
    GIANT_EAGLE = "Giant Eagle"
    GIANT_FROG = "Giant Frog"
    GIANT_GOAT = "Giant Goat"
    GIANT_LIZARD = "Giant Lizard"
    GIANT_OCTOPUS = "Giant Octopus"
    GIANT_OWL = "Giant Owl"
    GIANT_POISONOUS_SNAKE = "Giant Poisonous Snake"
    GIANT_RAT = "Giant Rat"
    GIANT_SCORPION = "Giant Scorpion"
    GIANT_SHARK = "Giant Shark"
    GIANT_SPIDER = "Giant Spider"
    GIANT_TOAD = "Giant Toad"
    GIANT_VULTURE = "Giant Vulture"
    GIANT_WASP = "Giant Wasp"
    GIANT_WEASEL = "Giant Weasel"
    GIANT_WOLF_SPIDER = "Giant Wolf Spider"
    HAWK = "Hawk"
    HUNTER_SHARK = "Hunter Shark"
    LION = "Lion"
    MAMMOTH = "Mammoth"
    MASTIFF = "Mastiff"
    OWL = "Owl"
    PANTHER = "Panther"
    POISONOUS_SNAKE = "Poisonous Snake"
    POLAR_BEAR = "Polar Bear"
    RAT = "Rat"
    RAVEN = "Raven"
    REEF_SHARK = "Reef Shark"
    RIDING_HORSE = "Riding Horse"
    SABER_TOOTHED_TIGER = "Saber-Toothed Tiger"
    TIGER = "Tiger"
    WARHORSE = "Warhorse"
    WOLF = "Wolf"

    # Celestials
    COUATL = "Couatl"

    # Constructs
    ANIMATED_ARMOR = "Animated Armor"
    FLYING_SWORD = "Flying Sword"
    IRON_GOLEM = "Iron Golem"
    STONE_GOLEM = "Stone Golem"

    # Dragons
    ADULT_BLACK_DRAGON = "Adult Black Dragon"
    ADULT_BLUE_DRAGON = "Adult Blue Dragon"
    ADULT_GREEN_DRAGON = "Adult Green Dragon"
    ADULT_RED_DRAGON = "Adult Red Dragon"
    ADULT_WHITE_DRAGON = "Adult White Dragon"
    ANCIENT_BLACK_DRAGON = "Ancient Black Dragon"
    ANCIENT_BLUE_DRAGON = "Ancient Blue Dragon"
    ANCIENT_GREEN_DRAGON = "Ancient Green Dragon"
    ANCIENT_RED_DRAGON = "Ancient Red Dragon"
    ANCIENT_WHITE_DRAGON = "Ancient White Dragon"
    BLACK_DRAGON_WYRMLING = "Black Dragon Wyrmling"
    BLUE_DRAGON_WYRMLING = "Blue Dragon Wyrmling"
    GREEN_DRAGON_WYRMLING = "Green Dragon Wyrmling"
    RED_DRAGON_WYRMLING = "Red Dragon Wyrmling"
    WHITE_DRAGON_WYRMLING = "White Dragon Wyrmling"
    YOUNG_BLACK_DRAGON = "Young Black Dragon"
    YOUNG_BLUE_DRAGON = "Young Blue Dragon"
    YOUNG_GREEN_DRAGON = "Young Green Dragon"
    YOUNG_RED_DRAGON = "Young Red Dragon"
    YOUNG_WHITE_DRAGON = "Young White Dragon"

    # Elementals
    AIR_ELEMENTAL = "Air Elemental"
    EARTH_ELEMENTAL = "Earth Elemental"
    FIRE_ELEMENTAL = "Fire Elemental"
    WATER_ELEMENTAL = "Water Elemental"

    # Fiends
    BALOR = "Balor"
    BARBED_DEVIL = "Barbed Devil"
    BEARDED_DEVIL = "Bearded Devil"
    BONE_DEVIL = "Bone Devil"
    CHAIN_DEVIL = "Chain Devil"
    DRETCH = "Dretch"
    ERINYES = "Erinyes"
    GLABREZU = "Glabrezu"
    HEZROU = "Hezrou"
    HORNED_DEVIL = "Horned Devil"
    ICE_DEVIL = "Ice Devil"
    IMP = "Imp"
    LEMURE = "Lemure"
    MARILITH = "Marilith"
    NALFESHNEE = "Nalfeshnee"
    PIT_FIEND = "Pit Fiend"
    QUASIT = "Quasit"
    VROCK = "Vrock"

    # Giants
    CLOUD_GIANT = "Cloud Giant"
    FIRE_GIANT = "Fire Giant"
    FROST_GIANT = "Frost Giant"
    HILL_GIANT = "Hill Giant"
    OGRE = "Ogre"
    STONE_GIANT = "Stone Giant"
    STORM_GIANT = "Storm Giant"

    # Humanoids
    ACOLYTE = "Acolyte"
    ASSASSIN = "Assassin"
    BANDIT = "Bandit"
    BANDIT_CAPTAIN = "Bandit Captain"
    BERSERKER = "Berserker"
    COMMONER = "Commoner"
    CULTIST = "Cultist"
    CULT_FANATIC = "Cult Fanatic"
    GLADIATOR = "Gladiator"
    GUARD = "Guard"
    KNIGHT = "Knight"
    MAGE = "Mage"
    NOBLE = "Noble"
    ORC = "Orc"
    PRIEST = "Priest"
    SCOUT = "Scout"
    SPY = "Spy"
    THUG = "Thug"
    TRIBAL_WARRIOR = "Tribal Warrior"
    VETERAN = "Veteran"

    # Monstrosities
    BASILISK = "Basilisk"
    COCKATRICE = "Cockatrice"
    GRICK = "Grick"
    GRIFFON = "Griffon"
    HARPY = "Harpy"
    HIPPOGRIFF = "Hippogriff"
    HYDRA = "Hydra"
    MEDUSA = "Medusa"
    MINOTAUR = "Minotaur"
    OWLBEAR = "Owlbear"
    PHASE_SPIDER = "Phase Spider"
    REMORHAZ = "Remorhaz"
    ROC = "Roc"
    WINTER_WOLF = "Winter Wolf"
    WORG = "Worg"

    # Oozes
    BLACK_PUDDING = "Black Pudding"
    GELATINOUS_CUBE = "Gelatinous Cube"
    GRAY_OOZE = "Gray Ooze"
    OCHRE_JELLY = "Ochre Jelly"

    # Plants
    SHAMBLING_MOUND = "Shambling Mound"
    TREANT = "Treant"

    # Undead
    GHOST = "Ghost"
    GHOUL = "Ghoul"
    LICH = "Lich"
    MUMMY = "Mummy"
    MUMMY_LORD = "Mummy Lord"
    SKELETON = "Skeleton"
    SPECTER = "Specter"
    VAMPIRE = "Vampire"
    WIGHT = "Wight"
    WRAITH = "Wraith"
    ZOMBIE = "Zombie"
