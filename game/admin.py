from django.contrib import admin

from game.models import Character, Game, PendingAction, Tale


class GameAdmin(admin.ModelAdmin):
    fields = ["name", "status"]
    list_display = ["name", "status", "start_date", "end_date"]


class CharacterAdmin(admin.ModelAdmin):
    fields = ["game", "name", "race", "user"]
    list_display = ["name", "race", "game", "user"]


class TaleAdmin(admin.ModelAdmin):
    fields = ["game", "description"]
    list_display = ["description", "game", "date"]


class PendingActionAdmin(admin.ModelAdmin):
    fields = ["game", "character", "action_type"]
    list_display = fields


admin.site.register(Game, GameAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(Tale, TaleAdmin)
admin.site.register(PendingAction, PendingActionAdmin)
