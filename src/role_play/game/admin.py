from django.contrib import admin

from .models.game import Game, Player


class GameAdmin(admin.ModelAdmin):
    fields = ["name", "state"]
    list_display = ["name", "state", "master", "start_date"]


class PlayerAdmin(admin.ModelAdmin):
    fields = ["character", "game"]
    list_display = fields


admin.site.register(Game, GameAdmin)
admin.site.register(Player, PlayerAdmin)
