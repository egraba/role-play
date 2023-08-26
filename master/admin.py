from django.contrib import admin

import master.models as mmodels


class CampaignAdmin(admin.ModelAdmin):
    fields = ["title", "slug", "synopsis", "main_conflict", "objective"]
    list_display = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(mmodels.Campaign, CampaignAdmin)
