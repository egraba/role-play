import secrets

import dj_database_url

from role_play.settings.base import *

SECRET_KEY = secrets.token_urlsafe(50)

DEBUG = True  # Enable debug for ephemeral testing

# Security - relaxed for ephemeral environment
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", "role-play-ephemeral.fly.dev"]
CSRF_TRUSTED_ORIGINS = ["https://role-play-ephemeral.fly.dev", "http://role-play-ephemeral.fly.dev"]
CSRF_COOKIE_SECURE = False  # Allow HTTP for testing
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False  # Allow HTTP for testing
SECURE_HSTS_SECONDS = 0  # Disable HSTS for ephemeral
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

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
            "hosts": [f"redis://default:{os.environ['REDIS_PASSWORD']}@fly-role-play-ephemeral-redis.upstash.io:6379"],
        },
    },
}

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "role-play-ephemeral",
        "USER": "postgres",
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": "role-play-ephemeral-db.internal",
        "PORT": "5433",
    }
}

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://default:{os.environ['REDIS_PASSWORD']}@fly-role-play-ephemeral-redis.upstash.io:6379",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# Celery
CELERY_BROKER_URL = f"redis://default:{os.environ['REDIS_PASSWORD']}@fly-role-play-ephemeral-redis.upstash.io:6379"
CELERY_RESULT_BACKEND = f"redis://default:{os.environ['REDIS_PASSWORD']}@fly-role-play-ephemeral-redis.upstash.io:6379"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Email backend - use console backend for ephemeral testing
DEFAULT_FROM_EMAIL = "ephemeral@egrabaroleplay.org"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  # Log emails to console

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR / "staticfiles"

# Update database configuration from $DATABASE_URL.
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES["default"].update(db_from_env)

# Logging - more verbose for debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
