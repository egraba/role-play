from django.contrib import admin

import chat.models as cmodels


class RoomAdmin(admin.ModelAdmin):
    list_display = ["game"]


class MessageAdmin(admin.ModelAdmin):
    fields = ["date", "user", "content"]
    list_display = fields


admin.site.register(cmodels.Room, RoomAdmin)
admin.site.register(cmodels.Message, MessageAdmin)
