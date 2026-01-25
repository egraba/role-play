import sentry_sdk
import secrets

import dj_database_url

from role_play.settings.base import *

SECRET_KEY = secrets.token_urlsafe(50)

DEBUG = False

# Security
# Include .fly.dev and .internal for Fly's private network
# Use * to allow health checks from any internal IP
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["https://role-play.fly.dev"]
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "role_play.wsgi.application"

# Channels
ASGI_APPLICATION = "role_play.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [f"redis://default:{os.environ['REDIS_PASSWORD']}@fly-role-play-redis.upstash.io:6379"],
        },
    },
}

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "role-play",
        "USER": "postgres",
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": "role-play-db.internal",
        "PORT": "5433",
    }
}

# Cache (using local memory - Redis still needed for Channels)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Email backend
DEFAULT_FROM_EMAIL = "grandmaster@egrabaroleplay.org"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = "587"
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 10
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR / "staticfiles"

# Update database configuration from $DATABASE_URL.
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES["default"].update(db_from_env)

# Sentry
sentry_sdk.init(
    dsn="https://40c2965ccfcc77646efabdb60a8bcaf5@o4507867128201216.ingest.us.sentry.io/4510585279152128",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)
