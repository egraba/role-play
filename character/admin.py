from django.contrib import admin

import character.models as cmodels


class CharacterAdmin(admin.ModelAdmin):
    fields = ["name", "race"]
    list_display = ["name", "race"]


admin.site.register(cmodels.Character, CharacterAdmin)
