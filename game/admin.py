from django.contrib import admin

from game.models import Character, Event, Game, PendingAction, Tale


class GameAdmin(admin.ModelAdmin):
    fields = ["name", "status", "user"]
    list_display = ["name", "status", "user", "start_date", "end_date"]


class CharacterAdmin(admin.ModelAdmin):
    fields = ["game", "name", "race", "user"]
    list_display = ["name", "race", "game", "user"]


class TaleAdmin(admin.ModelAdmin):
    fields = ["game", "description"]
    list_display = ["game", "description", "date"]


class EventAdmin(admin.ModelAdmin):
    fields = ["game", "message"]
    list_display = ["game", "date", "message"]


class PendingActionAdmin(admin.ModelAdmin):
    fields = ["game", "character", "action_type"]
    list_display = fields


admin.site.register(Game, GameAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(Tale, TaleAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(PendingAction, PendingActionAdmin)
