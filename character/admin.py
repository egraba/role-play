from django.contrib import admin

from .models.advancement import Advancement
from .models.character import Character
from .models.classes import ClassAdvancement, HitPoints
from .models.races import Sense


class CharacterAdmin(admin.ModelAdmin):
    fields = ["name", "user", "race", "class_name"]
    list_display = ["name", "user", "race", "class_name", "level", "xp"]


class AdvancementAdmin(admin.ModelAdmin):
    fields = ["xp", "level", "proficiency_bonus"]
    list_display = ["xp", "level", "proficiency_bonus"]


class SenseAdmin(admin.ModelAdmin):
    fields = ["name", "description"]
    list_display = ["name", "description"]


class HitPointsAdmin(admin.ModelAdmin):
    fields = ["class_feature", "hit_dice", "hp_first_level", "hp_higher_levels"]
    list_display = ["class_feature", "hit_dice", "hp_first_level", "hp_higher_levels"]


class ClassAdvancementAdmin(admin.ModelAdmin):
    fields = ["class_name", "level", "proficiency_bonus"]
    list_display = ["class_name", "level", "proficiency_bonus"]
    ordering = ["class_name", "level"]


# Character
admin.site.register(Character, CharacterAdmin)

# Advancement
admin.site.register(Advancement, AdvancementAdmin)

# Races
admin.site.register(Sense, SenseAdmin)

# Classes
admin.site.register(HitPoints, HitPointsAdmin)
admin.site.register(ClassAdvancement, ClassAdvancementAdmin)
