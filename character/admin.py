from django.contrib import admin

from .models.advancement import Advancement
from .models.character import Character
from .models.classes import ClassAdvancement, HitPoints, Proficiencies
from .models.races import RacialTrait, Sense


class CharacterAdmin(admin.ModelAdmin):
    fields = ["name", "user", "race", "class_name"]
    list_display = ["name", "user", "race", "class_name", "level", "xp"]


class AdvancementAdmin(admin.ModelAdmin):
    fields = ["xp", "level", "proficiency_bonus"]
    list_display = ["xp", "level", "proficiency_bonus"]


class SenseAdmin(admin.ModelAdmin):
    fields = ["name", "description"]
    list_display = ["name", "description"]


class RacialTraitAdmin(admin.ModelAdmin):
    fields = [
        "race",
        "adult_age",
        "life_expectancy",
        "alignment",
        "size",
        "speed",
        "languages",
        "senses",
    ]
    list_display = [
        "race",
        "adult_age",
        "life_expectancy",
        "alignment",
        "size",
        "speed",
    ]


class HitPointsAdmin(admin.ModelAdmin):
    fields = ["class_feature", "hit_dice", "hp_first_level", "hp_higher_levels"]
    list_display = ["class_feature", "hit_dice", "hp_first_level", "hp_higher_levels"]


class ProficienciesAdmin(admin.ModelAdmin):
    fields = ["class_feature", "armor", "weapons", "tools", "saving_throws", "skills"]
    list_display = [
        "class_feature",
        "armor",
        "weapons",
        "tools",
        "saving_throws",
        "skills",
    ]


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
admin.site.register(RacialTrait, RacialTraitAdmin)

# Classes
admin.site.register(HitPoints, HitPointsAdmin)
admin.site.register(Proficiencies, ProficienciesAdmin)
admin.site.register(ClassAdvancement, ClassAdvancementAdmin)
