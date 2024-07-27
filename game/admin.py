from django.contrib import admin

from .models.events import QuestUpdate
from .models.game import Game, Player


class GameAdmin(admin.ModelAdmin):
    fields = ["name", "state", "master"]
    list_display = ["name", "state", "master", "start_date"]


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
admin.site.register(QuestUpdate, QuestAdmin)
