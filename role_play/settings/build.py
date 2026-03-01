"""
Minimal settings for Docker build-time collectstatic.

These dummy credentials are intentional — this file is only used during
`docker build` to collect static files into the image. Never use in production.
"""

from role_play.settings.base import *

SECRET_KEY = "build-time-dummy-key-not-for-production"

DEBUG = False
ALLOWED_HOSTS: list[str] = []

STATIC_ROOT = BASE_DIR / "staticfiles"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}
