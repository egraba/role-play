"""
Magic item constants for D&D 5e SRD.

Rarity levels determine item power and value:
- Common: Minor magical effects, widely available
- Uncommon: Useful magic, found in most treasure hoards
- Rare: Significant power, sought after by adventurers
- Very Rare: Powerful magic, rare even in large cities
- Legendary: World-changing artifacts, unique items
"""

from django.db.models import TextChoices


class Rarity(TextChoices):
    """Magic item rarity levels per D&D 5e SRD."""

    COMMON = "common", "Common"
    UNCOMMON = "uncommon", "Uncommon"
    RARE = "rare", "Rare"
    VERY_RARE = "very_rare", "Very Rare"
    LEGENDARY = "legendary", "Legendary"


class MagicItemType(TextChoices):
    """Categories of magic items per D&D 5e SRD."""

    ARMOR = "armor", "Armor"
    POTION = "potion", "Potion"
    RING = "ring", "Ring"
    ROD = "rod", "Rod"
    SCROLL = "scroll", "Scroll"
    STAFF = "staff", "Staff"
    WAND = "wand", "Wand"
    WEAPON = "weapon", "Weapon"
    WONDROUS = "wondrous", "Wondrous Item"


class MagicWeaponBonus(TextChoices):
    """Enhancement bonuses for magic weapons."""

    PLUS_1 = "+1", "+1"
    PLUS_2 = "+2", "+2"
    PLUS_3 = "+3", "+3"


class MagicArmorBonus(TextChoices):
    """Enhancement bonuses for magic armor."""

    PLUS_1 = "+1", "+1"
    PLUS_2 = "+2", "+2"
    PLUS_3 = "+3", "+3"


class MagicItemName(TextChoices):
    """
    Magic item names from D&D 5e SRD.

    Organized by type for easier reference.
    """

    # +1/+2/+3 Weapons (various base weapons)
    WEAPON_PLUS_1 = "Weapon +1"
    WEAPON_PLUS_2 = "Weapon +2"
    WEAPON_PLUS_3 = "Weapon +3"

    # +1/+2/+3 Armor (various base armors)
    ARMOR_PLUS_1 = "Armor +1"
    ARMOR_PLUS_2 = "Armor +2"
    ARMOR_PLUS_3 = "Armor +3"

    # +1/+2/+3 Shields
    SHIELD_PLUS_1 = "Shield +1"
    SHIELD_PLUS_2 = "Shield +2"
    SHIELD_PLUS_3 = "Shield +3"

    # Potions
    POTION_OF_HEALING = "Potion of Healing"
    POTION_OF_GREATER_HEALING = "Potion of Greater Healing"
    POTION_OF_SUPERIOR_HEALING = "Potion of Superior Healing"
    POTION_OF_SUPREME_HEALING = "Potion of Supreme Healing"

    # Wands
    WAND_OF_MAGIC_MISSILES = "Wand of Magic Missiles"
    WAND_OF_THE_WAR_MAGE_PLUS_1 = "Wand of the War Mage +1"
    WAND_OF_THE_WAR_MAGE_PLUS_2 = "Wand of the War Mage +2"
    WAND_OF_THE_WAR_MAGE_PLUS_3 = "Wand of the War Mage +3"

    # Staffs
    STAFF_OF_THE_MAGI = "Staff of the Magi"
    STAFF_OF_POWER = "Staff of Power"
    STAFF_OF_HEALING = "Staff of Healing"
    STAFF_OF_THE_WOODLANDS = "Staff of the Woodlands"

    # Rings
    RING_OF_PROTECTION = "Ring of Protection"
    RING_OF_SPELL_STORING = "Ring of Spell Storing"

    # Wondrous Items
    AMULET_OF_HEALTH = "Amulet of Health"
    BAG_OF_HOLDING = "Bag of Holding"
    BOOTS_OF_ELVENKIND = "Boots of Elvenkind"
    BOOTS_OF_SPEED = "Boots of Speed"
    BRACERS_OF_DEFENSE = "Bracers of Defense"
    CLOAK_OF_ELVENKIND = "Cloak of Elvenkind"
    CLOAK_OF_PROTECTION = "Cloak of Protection"
    GAUNTLETS_OF_OGRE_POWER = "Gauntlets of Ogre Power"
    HEADBAND_OF_INTELLECT = "Headband of Intellect"
    PEARL_OF_POWER = "Pearl of Power"
