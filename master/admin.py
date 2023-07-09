from django.contrib import admin

import master.models as mmodels


class StoryAdmin(admin.ModelAdmin):
    fields = ["title", "synopsis", "main_conflict"]


admin.site.register(mmodels.Story, StoryAdmin)
