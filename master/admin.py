from django.contrib import admin

import master.models as mmodels


class StoryAdmin(admin.ModelAdmin):
    fields = ["title", "slug", "synopsis", "main_conflict"]
    list_display = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(mmodels.Story, StoryAdmin)
