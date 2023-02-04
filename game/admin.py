from django.contrib import admin

from game.models import Character, Game, Narrative, PendingAction


class GameAdmin(admin.ModelAdmin):
    fields = ["name"]


class CharacterAdmin(admin.ModelAdmin):
    fields = ["game", "name", "race"]


class NarrativeAdmin(admin.ModelAdmin):
    fields = ["game", "message"]


class PendingActionAdmin(admin.ModelAdmin):
    fields = ["game", "narrative", "character", "action_type"]


admin.site.register(Game, GameAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(Narrative, NarrativeAdmin)
admin.site.register(PendingAction, PendingActionAdmin)
