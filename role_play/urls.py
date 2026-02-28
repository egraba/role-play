from django.conf import settings
from django.contrib import admin
from django.db import connection
from django.db.utils import OperationalError
from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import RedirectView

from user.views import RateLimitedLoginView


def health_check(request):
    """Health check endpoint for Fly.io — probes the database connection."""
    try:
        connection.ensure_connection()
    except OperationalError:
        return JsonResponse({"status": "error"}, status=503)
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("game/", include("game.urls")),
    path("master/", include("master.urls")),
    path("character/", include("character.urls")),
    path("admin/", admin.site.urls),
    path("accounts/login/", RateLimitedLoginView.as_view(), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", RedirectView.as_view(url="game/", permanent=True)),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
