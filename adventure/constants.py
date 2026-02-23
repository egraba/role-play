from django.db import models


class SceneType(models.TextChoices):
    COMBAT = "C", "Combat"
    SOCIAL = "S", "Social Interaction"
    EXPLORATION = "E", "Exploration"
    REST = "R", "Rest"
    TRANSITION = "T", "Transition"


class EncounterType(models.TextChoices):
    COMBAT = "C", "Combat"
    SOCIAL = "S", "Social"
    TRAP = "T", "Trap"
    PUZZLE = "P", "Puzzle"
    EXPLORATION = "E", "Exploration"


class Difficulty(models.TextChoices):
    EASY = "E", "Easy"
    MEDIUM = "M", "Medium"
    HARD = "H", "Hard"
    DEADLY = "D", "Deadly"


class Tone(models.TextChoices):
    HEROIC = "heroic", "Heroic"
    DARK = "dark", "Dark"
    COMEDIC = "comedic", "Comedic"
    MYSTERY = "mystery", "Mystery"
    HORROR = "horror", "Horror"


class Region(models.TextChoices):
    DUNGEON = "dungeon", "Dungeon"
    CITY = "city", "City"
    WILDERNESS = "wilderness", "Wilderness"
    SEA = "sea", "Sea"
    PLANAR = "planar", "Planar"
    UNDERDARK = "underdark", "Underdark"
