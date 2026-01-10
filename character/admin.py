from django.contrib import admin

from .models.advancement import Advancement
from .models.character import Character
from .models.klasses import HitPoints, KlassAdvancement
from .models.species import Species, SpeciesTrait


class CharacterAdmin(admin.ModelAdmin):
    fields = ["name", "user", "species", "klass"]
    list_display = ["name", "user", "species", "klass", "level", "xp"]


class AdvancementAdmin(admin.ModelAdmin):
    fields = ["xp", "level", "proficiency_bonus"]
    list_display = ["xp", "level", "proficiency_bonus"]


class SpeciesAdmin(admin.ModelAdmin):
    fields = [
        "name",
        "size",
        "speed",
        "darkvision",
        "traits",
        "languages",
        "description",
    ]
    list_display = ["name", "size", "speed", "darkvision"]
    filter_horizontal = ["traits", "languages"]


class SpeciesTraitAdmin(admin.ModelAdmin):
    fields = ["name", "description"]
    list_display = ["name", "description"]


class HitPointsAdmin(admin.ModelAdmin):
    fields = ["klass_feature", "hit_dice", "hp_first_level", "hp_higher_levels"]
    list_display = ["klass_feature", "hit_dice", "hp_first_level", "hp_higher_levels"]


class KlassAdvancementAdmin(admin.ModelAdmin):
    fields = ["klass", "level", "proficiency_bonus"]
    list_display = ["klass", "level", "proficiency_bonus"]
    ordering = ["klass", "level"]


# Character
admin.site.register(Character, CharacterAdmin)

# Advancement
admin.site.register(Advancement, AdvancementAdmin)

# Species
admin.site.register(Species, SpeciesAdmin)
admin.site.register(SpeciesTrait, SpeciesTraitAdmin)

# Classes
admin.site.register(HitPoints, HitPointsAdmin)
admin.site.register(KlassAdvancement, KlassAdvancementAdmin)
