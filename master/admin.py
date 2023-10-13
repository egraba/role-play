from django.contrib import admin

from master.models import Campaign


class CampaignAdmin(admin.ModelAdmin):
    fields = ["title", "slug", "synopsis", "main_conflict", "objective"]
    list_display = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Campaign, CampaignAdmin)
