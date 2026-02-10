from django.db.models import IntegerChoices, TextChoices


class SpellSchool(TextChoices):
    """D&D 5e schools of magic."""

    ABJURATION = "abjuration", "Abjuration"
    CONJURATION = "conjuration", "Conjuration"
    DIVINATION = "divination", "Divination"
    ENCHANTMENT = "enchantment", "Enchantment"
    EVOCATION = "evocation", "Evocation"
    ILLUSION = "illusion", "Illusion"
    NECROMANCY = "necromancy", "Necromancy"
    TRANSMUTATION = "transmutation", "Transmutation"


class SpellLevel(IntegerChoices):
    """D&D 5e spell levels (0 = cantrip)."""

    CANTRIP = 0, "Cantrip"
    FIRST = 1, "1st Level"
    SECOND = 2, "2nd Level"
    THIRD = 3, "3rd Level"
    FOURTH = 4, "4th Level"
    FIFTH = 5, "5th Level"
    SIXTH = 6, "6th Level"
    SEVENTH = 7, "7th Level"
    EIGHTH = 8, "8th Level"
    NINTH = 9, "9th Level"


class CastingTime(TextChoices):
    """Common D&D 5e casting times."""

    ACTION = "action", "1 Action"
    BONUS_ACTION = "bonus_action", "1 Bonus Action"
    REACTION = "reaction", "1 Reaction"
    MINUTE_1 = "1_minute", "1 Minute"
    MINUTES_10 = "10_minutes", "10 Minutes"
    HOUR_1 = "1_hour", "1 Hour"
    HOURS_8 = "8_hours", "8 Hours"
    HOURS_12 = "12_hours", "12 Hours"
    HOURS_24 = "24_hours", "24 Hours"


class SpellRange(TextChoices):
    """Common D&D 5e spell ranges."""

    SELF = "self", "Self"
    TOUCH = "touch", "Touch"
    FEET_5 = "5_feet", "5 feet"
    FEET_10 = "10_feet", "10 feet"
    FEET_30 = "30_feet", "30 feet"
    FEET_60 = "60_feet", "60 feet"
    FEET_90 = "90_feet", "90 feet"
    FEET_120 = "120_feet", "120 feet"
    FEET_150 = "150_feet", "150 feet"
    FEET_300 = "300_feet", "300 feet"
    FEET_500 = "500_feet", "500 feet"
    MILE_1 = "1_mile", "1 mile"
    SIGHT = "sight", "Sight"
    UNLIMITED = "unlimited", "Unlimited"
    SPECIAL = "special", "Special"


class SpellDuration(TextChoices):
    """Common D&D 5e spell durations."""

    INSTANTANEOUS = "instantaneous", "Instantaneous"
    ROUND_1 = "1_round", "1 round"
    MINUTE_1 = "1_minute", "1 minute"
    MINUTES_10 = "10_minutes", "10 minutes"
    HOUR_1 = "1_hour", "1 hour"
    HOURS_8 = "8_hours", "8 hours"
    HOURS_24 = "24_hours", "24 hours"
    DAYS_7 = "7_days", "7 days"
    DAYS_10 = "10_days", "10 days"
    DAYS_30 = "30_days", "30 days"
    UNTIL_DISPELLED = "until_dispelled", "Until dispelled"
    SPECIAL = "special", "Special"


class SpellComponent(TextChoices):
    """D&D 5e spell components."""

    VERBAL = "V", "Verbal"
    SOMATIC = "S", "Somatic"
    MATERIAL = "M", "Material"


class CasterType(TextChoices):
    """Types of spellcasters based on how they access spells."""

    PREPARED = "prepared", "Prepared"  # Cleric, Druid, Paladin, Wizard
    KNOWN = "known", "Known"  # Bard, Ranger, Sorcerer, Warlock
    PACT = "pact", "Pact"  # Warlock Pact Magic


class SpellcastingAbility(TextChoices):
    """Spellcasting ability by class."""

    INTELLIGENCE = "intelligence", "Intelligence"  # Wizard
    WISDOM = "wisdom", "Wisdom"  # Cleric, Druid, Ranger
    CHARISMA = "charisma", "Charisma"  # Bard, Paladin, Sorcerer, Warlock


class SpellEffectType(TextChoices):
    """Types of effects a spell can have."""

    DAMAGE = "damage", "Damage"
    HEALING = "healing", "Healing"
    CONDITION = "condition", "Condition"
    BUFF = "buff", "Buff"
    DEBUFF = "debuff", "Debuff"
    SUMMON = "summon", "Summon"
    UTILITY = "utility", "Utility"


class SpellTargetType(TextChoices):
    """How a spell targets creatures or areas."""

    SELF = "self", "Self"
    SINGLE = "single", "Single Target"
    MULTIPLE = "multiple", "Multiple Targets"
    AREA = "area", "Area"
    LINE = "line", "Line"
    CONE = "cone", "Cone"


class SpellSaveType(TextChoices):
    """Saving throw types for spells."""

    NONE = "none", "None"
    STRENGTH = "STR", "Strength"
    DEXTERITY = "DEX", "Dexterity"
    CONSTITUTION = "CON", "Constitution"
    INTELLIGENCE = "INT", "Intelligence"
    WISDOM = "WIS", "Wisdom"
    CHARISMA = "CHA", "Charisma"


class SpellSaveEffect(TextChoices):
    """What happens on a successful save."""

    NONE = "none", "None"
    HALF_DAMAGE = "half_damage", "Half Damage"
    NEGATES = "negates", "Negates"


class SpellDamageType(TextChoices):
    """Damage types for spells."""

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


class EffectDurationType(TextChoices):
    """Duration types for spell effects."""

    INSTANTANEOUS = "instantaneous", "Instantaneous"
    ROUNDS = "rounds", "Rounds"
    MINUTES = "minutes", "Minutes"
    HOURS = "hours", "Hours"
    UNTIL_DISPELLED = "until_dispelled", "Until Dispelled"
    CONCENTRATION = "concentration", "Concentration"
