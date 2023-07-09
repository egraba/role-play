from django.contrib import admin

import character.models as cmodels


class CharacterAdmin(admin.ModelAdmin):
    fields = ["name", "race", "player"]
    list_display = ["name", "race", "player"]


admin.site.register(cmodels.Character, CharacterAdmin)
