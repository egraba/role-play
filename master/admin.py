from django.contrib import admin

import master.models as mmodels


class BackgroundStoryAdmin(admin.ModelAdmin):
    fields = ["name", "status", "master"]


admin.site.register(mmodels.Story, BackgroundStoryAdmin)
