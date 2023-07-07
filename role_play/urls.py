from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("game/", include("game.urls")),
    path("master/", include("master.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", RedirectView.as_view(url="game/", permanent=True)),
    # path("__debug__/", include("debug_toolbar.urls")),
]
