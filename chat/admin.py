from django.contrib import admin

import chat.models as cmodels


class MessageAdmin(admin.ModelAdmin):
    fields = ["date", "character", "content"]
    list_display = fields


admin.site.register(cmodels.Message, MessageAdmin)
