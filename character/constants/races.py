from django.db.models import TextChoices


class Size(TextChoices):
    SMALL = "S", "Small"
    MEDIUM = "M", "Medium"


class LanguageName(TextChoices):
    COMMON = "common", "Common"
    DWARVISH = "dwarvish", "Dwarvish"
    ELVISH = "elvish", "Elvish"
    GIANT = "giant", "Giant"
    GNOMISH = "gnomish", "Gnomish"
    GOBLIN = "goblin", "Goblin"
    HALFLING = "halfling", "Halfling"
    ORC = "orc", "Orc"
    ABYSSAL = "abyssal", "Abyssal"
    CELESTIAL = "celestial", "Celestial"
    DEEP_SPEECH = "deep_speech", "Deep Speech"
    DRACONIC = "draconic", "Draconic"
    INFERNAL = "infernal", "Infernal"
    PRIMORDIAL = "primordial", "Primordial"
    SYLVAN = "sylvan", "Sylvan"
    UNDERCOMMON = "undercommon", "Undercommon"


class LanguageType(TextChoices):
    STANDARD = "S", "Standard"
    EXOTIC = "E", "Exotic"
