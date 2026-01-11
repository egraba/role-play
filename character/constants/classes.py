from django.db.models import TextChoices


class ClassName(TextChoices):
    """D&D 2024 SRD character class names."""

    BARBARIAN = "barbarian", "Barbarian"
    BARD = "bard", "Bard"
    CLERIC = "cleric", "Cleric"
    DRUID = "druid", "Druid"
    FIGHTER = "fighter", "Fighter"
    MONK = "monk", "Monk"
    PALADIN = "paladin", "Paladin"
    RANGER = "ranger", "Ranger"
    ROGUE = "rogue", "Rogue"
    SORCERER = "sorcerer", "Sorcerer"
    WARLOCK = "warlock", "Warlock"
    WIZARD = "wizard", "Wizard"


class WeaponCategory(TextChoices):
    """Weapon proficiency categories."""

    SIMPLE = "simple", "Simple Weapons"
    MARTIAL = "martial", "Martial Weapons"
