from django.contrib import admin

from game.models import Character, Game, PendingAction, Tale


class GameAdmin(admin.ModelAdmin):
    fields = ["name", "status"]


class CharacterAdmin(admin.ModelAdmin):
    fields = ["game", "name", "race", "user"]


class TaleAdmin(admin.ModelAdmin):
    fields = ["game", "description"]


class PendingActionAdmin(admin.ModelAdmin):
    fields = ["game", "character", "action_type"]


admin.site.register(Game, GameAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(Tale, TaleAdmin)
admin.site.register(PendingAction, PendingActionAdmin)
