from django.contrib import admin

import character.models as cmodels


class CharacterAdmin(admin.ModelAdmin):
    fields = ["name", "user", "race"]
    list_display = ["name", "user", "race"]


admin.site.register(cmodels.Character, CharacterAdmin)
