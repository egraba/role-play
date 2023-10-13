from django.contrib import admin

from character.models import Ability, Advancement, Character, ClassAdvancement


class CharacterAdmin(admin.ModelAdmin):
    fields = ["name", "user", "race", "class_name"]
    list_display = ["name", "user", "race", "class_name", "level", "xp"]


class AdvancementAdmin(admin.ModelAdmin):
    fields = ["xp", "level", "proficiency_bonus"]
    list_display = ["xp", "level", "proficiency_bonus"]


class AbilityAdmin(admin.ModelAdmin):
    fields = ["name", "description"]
    list_display = ["name", "description"]


class ClassAdvancementAdmin(admin.ModelAdmin):
    fields = ["class_name", "level", "proficiency_bonus"]
    list_display = ["class_name", "level", "proficiency_bonus"]
    ordering = ["class_name", "level"]


admin.site.register(Character, CharacterAdmin)
admin.site.register(Advancement, AdvancementAdmin)
admin.site.register(Ability, AbilityAdmin)
admin.site.register(ClassAdvancement, ClassAdvancementAdmin)
