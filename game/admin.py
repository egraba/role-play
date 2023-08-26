from django.contrib import admin

import game.models as gmodels


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


admin.site.register(gmodels.Game, GameAdmin)
admin.site.register(gmodels.Player, PlayerAdmin)
admin.site.register(gmodels.Quest, QuestAdmin)
admin.site.register(gmodels.Event, EventAdmin)
