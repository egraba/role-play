from django.contrib import admin

import character.models as cmodels


class CharacterAdmin(admin.ModelAdmin):
    fields = ["name", "user", "race"]
    list_display = ["name", "user", "race"]


class AdvancementAdmin(admin.ModelAdmin):
    fields = ["xp", "level", "proficiency_bonus"]
    list_display = ["xp", "level", "proficiency_bonus"]


admin.site.register(cmodels.Character, CharacterAdmin)
admin.site.register(cmodels.Advancement, AdvancementAdmin)
