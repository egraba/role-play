from django.contrib import admin

import game.models as gmodels


class GameAdmin(admin.ModelAdmin):
    fields = ["name", "status", "master"]
    list_display = ["name", "status", "master", "start_date", "end_date"]


class PlayerAdmin(admin.ModelAdmin):
    fields = ["character", "game"]
    list_display = fields


class TaleAdmin(admin.ModelAdmin):
    fields = ["game", "description"]
    list_display = ["game", "content", "date"]


class EventAdmin(admin.ModelAdmin):
    fields = ["game", "message"]
    list_display = ["game", "date", "message"]


class PendingActionAdmin(admin.ModelAdmin):
    fields = ["game", "character", "action_type"]
    list_display = fields


admin.site.register(gmodels.Game, GameAdmin)
admin.site.register(gmodels.Player, PlayerAdmin)
admin.site.register(gmodels.Tale, TaleAdmin)
admin.site.register(gmodels.Event, EventAdmin)
admin.site.register(gmodels.PendingAction, PendingActionAdmin)
