from role_play.settings.base import *

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DEBUG = True

ALLOWED_HOSTS = []  # type: list

INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
] + MIDDLEWARE

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
            "debug": True,
        },
    },
]

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "role-play",
        "USER": "devuser",
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# Channels
ASGI_APPLICATION = "role_play.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": ["redis://127.0.0.1:6379"],
        },
    },
}

# Celery
CELERY_BROKER_URL = "redis://127.0.0.1:6379"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Email backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Necessary for Django Debug Toolbar
INTERNAL_IPS = [
    "127.0.0.1",
]
