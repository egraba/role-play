"""
Test-specific Django settings optimized for faster test execution.

Key optimizations:
- MD5PasswordHasher: Much faster than default password hashers
- In-memory channel layer: Avoids Redis overhead for tests
- SQLite: Uses in-memory SQLite database for faster tests

These settings are self-contained with no external dependencies (no Doppler,
no env vars) so that tests run identically in local development and CI,
including Dependabot PRs which have no access to repository secrets.
"""

from role_play.settings.base import *

SECRET_KEY = "test-secret-key-not-for-production"  # noqa: S105

DEBUG = True

ALLOWED_HOSTS: list[str] = []

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
            "debug": True,
        },
    },
]

# Database - in-memory SQLite for speed
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Cache (dummy for tests)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Use in-memory channel layer for tests (faster than Redis)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# Email backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Use a faster password hasher for tests
# MD5 is insecure for production but perfectly fine for testing
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable logging during tests for speed
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
        "level": "CRITICAL",
    },
}
