from django.contrib import admin

import character.models as cmodels


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


admin.site.register(cmodels.Character, CharacterAdmin)
admin.site.register(cmodels.Advancement, AdvancementAdmin)
admin.site.register(cmodels.Ability, AbilityAdmin)
admin.site.register(cmodels.ClassAdvancement, ClassAdvancementAdmin)
