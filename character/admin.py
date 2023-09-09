from django.contrib import admin

import character.models as cmodels


class CharacterAdmin(admin.ModelAdmin):
    fields = ["name", "user", "race"]
    list_display = ["name", "user", "race", "xp"]


class AdvancementAdmin(admin.ModelAdmin):
    fields = ["xp", "level", "proficiency_bonus"]
    list_display = ["xp", "level", "proficiency_bonus"]


class AbilityAdmin(admin.ModelAdmin):
    fields = ["name", "description"]
    list_display = ["name", "description"]


admin.site.register(cmodels.Character, CharacterAdmin)
admin.site.register(cmodels.Advancement, AdvancementAdmin)
admin.site.register(cmodels.Ability, AbilityAdmin)
