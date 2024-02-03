from django.contrib import admin

from .models.events import Event, Quest
from .models.game import Game, Player


class GameAdmin(admin.ModelAdmin):
    fields = ["name", "status", "master"]
    list_display = ["name", "status", "master", "start_date"]


class PlayerAdmin(admin.ModelAdmin):
    fields = ["character", "game"]
    list_display = fields


class QuestAdmin(admin.ModelAdmin):
    fields = ["game", "description"]
    list_display = ["game", "content", "date"]


class EventAdmin(admin.ModelAdmin):
    fields = ["game", "message"]
    list_display = ["game", "date", "message"]


admin.site.register(Game, GameAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Quest, QuestAdmin)
admin.site.register(Event, EventAdmin)
