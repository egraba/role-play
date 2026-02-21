from django.db.models import TextChoices


class SpeciesName(TextChoices):
    DRAGONBORN = "dragonborn", "Dragonborn"
    DWARF = "dwarf", "Dwarf"
    ELF = "elf", "Elf"
    GNOME = "gnome", "Gnome"
    GOLIATH = "goliath", "Goliath"
    HALFLING = "halfling", "Halfling"
    HUMAN = "human", "Human"
    ORC = "orc", "Orc"
    TIEFLING = "tiefling", "Tiefling"


class SpeciesTraitName(TextChoices):
    # Dragonborn traits
    BREATH_WEAPON = "breath_weapon", "Breath Weapon"
    DRACONIC_ANCESTRY = "draconic_ancestry", "Draconic Ancestry"
    DRACONIC_DAMAGE_RESISTANCE = (
        "draconic_damage_resistance",
        "Draconic Damage Resistance",
    )
    DRACONIC_FLIGHT = "draconic_flight", "Draconic Flight"
    # Dwarf traits
    DWARVEN_RESILIENCE = "dwarven_resilience", "Dwarven Resilience"
    DWARVEN_TOUGHNESS = "dwarven_toughness", "Dwarven Toughness"
    STONECUNNING = "stonecunning", "Stonecunning"
    # Elf traits
    FEY_ANCESTRY = "fey_ancestry", "Fey Ancestry"
    KEEN_SENSES = "keen_senses", "Keen Senses"
    TRANCE = "trance", "Trance"
    # Gnome traits
    GNOMISH_CUNNING = "gnomish_cunning", "Gnomish Cunning"
    GNOMISH_LINEAGE = "gnomish_lineage", "Gnomish Lineage"
    # Goliath traits
    GIANT_ANCESTRY = "giant_ancestry", "Giant Ancestry"
    LARGE_FORM = "large_form", "Large Form"
    POWERFUL_BUILD = "powerful_build", "Powerful Build"
    # Halfling traits
    BRAVE = "brave", "Brave"
    HALFLING_NIMBLENESS = "halfling_nimbleness", "Halfling Nimbleness"
    LUCKY = "lucky", "Lucky"
    # Human traits
    RESOURCEFUL = "resourceful", "Resourceful"
    SKILLFUL = "skillful", "Skillful"
    VERSATILE = "versatile", "Versatile"
    # Orc traits
    ADRENALINE_RUSH = "adrenaline_rush", "Adrenaline Rush"
    RELENTLESS_ENDURANCE = "relentless_endurance", "Relentless Endurance"
    # Tiefling traits
    FIENDISH_LEGACY = "fiendish_legacy", "Fiendish Legacy"
    OTHERWORLDLY_PRESENCE = "otherworldly_presence", "Otherworldly Presence"
