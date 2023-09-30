from django.contrib import admin

from character.models.advancement import Advancement
from character.models.character import Character
from character.models.classes import ClassAdvancement, HitPoints, Proficiencies
from character.models.races import Ability, RacialTrait


class CharacterAdmin(admin.ModelAdmin):
    fields = ["name", "user", "race", "class_name"]
    list_display = ["name", "user", "race", "class_name", "level", "xp"]


class AdvancementAdmin(admin.ModelAdmin):
    fields = ["xp", "level", "proficiency_bonus"]
    list_display = ["xp", "level", "proficiency_bonus"]


class AbilityAdmin(admin.ModelAdmin):
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
        "abilities",
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
admin.site.register(Ability, AbilityAdmin)
admin.site.register(RacialTrait, RacialTraitAdmin)

# Classes
admin.site.register(HitPoints, HitPointsAdmin)
admin.site.register(Proficiencies, ProficienciesAdmin)
admin.site.register(ClassAdvancement, ClassAdvancementAdmin)
