from django.contrib import admin

from .models.advancement import Advancement
from .models.character import Character
from .models.klasses import KlassAdvancement, HitPoints
from .models.races import Sense


class CharacterAdmin(admin.ModelAdmin):
    fields = ["name", "user", "race", "klass"]
    list_display = ["name", "user", "race", "klass", "level", "xp"]


class AdvancementAdmin(admin.ModelAdmin):
    fields = ["xp", "level", "proficiency_bonus"]
    list_display = ["xp", "level", "proficiency_bonus"]


class SenseAdmin(admin.ModelAdmin):
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

# Races
admin.site.register(Sense, SenseAdmin)

# Classes
admin.site.register(HitPoints, HitPointsAdmin)
admin.site.register(KlassAdvancement, KlassAdvancementAdmin)
