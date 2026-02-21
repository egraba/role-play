from django.db.models import TextChoices


class FeatType(TextChoices):
    ORIGIN = "O", "Origin"
    GENERAL = "G", "General"


class FeatName(TextChoices):
    ALERT = "alert", "Alert"
    CRAFTER = "crafter", "Crafter"
    HEALER = "healer", "Healer"
    LUCKY = "lucky", "Lucky"
    MAGIC_INITIATE_BARD = "magic_initiate_bard", "Magic Initiate (Bard)"
    MAGIC_INITIATE_CLERIC = "magic_initiate_cleric", "Magic Initiate (Cleric)"
    MAGIC_INITIATE_DRUID = "magic_initiate_druid", "Magic Initiate (Druid)"
    MAGIC_INITIATE_SORCERER = "magic_initiate_sorcerer", "Magic Initiate (Sorcerer)"
    MAGIC_INITIATE_WARLOCK = "magic_initiate_warlock", "Magic Initiate (Warlock)"
    MAGIC_INITIATE_WIZARD = "magic_initiate_wizard", "Magic Initiate (Wizard)"
    MUSICIAN = "musician", "Musician"
    SAVAGE_ATTACKER = "savage_attacker", "Savage Attacker"
    SKILLED = "skilled", "Skilled"
    TAVERN_BRAWLER = "tavern_brawler", "Tavern Brawler"
    TOUGH = "tough", "Tough"
