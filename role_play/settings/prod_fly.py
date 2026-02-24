import sentry_sdk

import dj_database_url

from role_play.settings.base import *

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DEBUG = False

# Security
# Include .fly.dev and .internal for Fly's private network
# Use * to allow health checks from any internal IP
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["https://role-play.fly.dev"]
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year — required for HSTS preload list
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
                "game.context_processors.navbar_context",
            ],
        },
    },
]

WSGI_APPLICATION = "role_play.wsgi.application"

REDIS_URL = f"rediss://default:{os.environ['REDIS_PASSWORD']}@fly-role-play-redis.upstash.io:6380"

# Channels
ASGI_APPLICATION = "role_play.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
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

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
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

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR / "staticfiles"

# Update database configuration from $DATABASE_URL.
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES["default"].update(db_from_env)

# Sentry
sentry_sdk.init(
    dsn="https://40c2965ccfcc77646efabdb60a8bcaf5@o4507867128201216.ingest.us.sentry.io/4510585279152128",
    environment="production",
    traces_sample_rate=0.1,
)
