from django.db.models import TextChoices


class SpeciesName(TextChoices):
    DWARF = "dwarf", "Dwarf"
    ELF = "elf", "Elf"
    HALFLING = "halfling", "Halfling"
    HUMAN = "human", "Human"


class SpeciesTraitName(TextChoices):
    # Dwarf traits
    DWARVEN_RESILIENCE = "dwarven_resilience", "Dwarven Resilience"
    DWARVEN_TOUGHNESS = "dwarven_toughness", "Dwarven Toughness"
    STONECUNNING = "stonecunning", "Stonecunning"
    # Elf traits
    FEY_ANCESTRY = "fey_ancestry", "Fey Ancestry"
    KEEN_SENSES = "keen_senses", "Keen Senses"
    TRANCE = "trance", "Trance"
    # Halfling traits
    BRAVE = "brave", "Brave"
    HALFLING_NIMBLENESS = "halfling_nimbleness", "Halfling Nimbleness"
    LUCKY = "lucky", "Lucky"
    # Human traits
    RESOURCEFUL = "resourceful", "Resourceful"
    SKILLFUL = "skillful", "Skillful"
    VERSATILE = "versatile", "Versatile"
