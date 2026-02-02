"""
Test-specific Django settings optimized for faster test execution.

Key optimizations:
- MD5PasswordHasher: Much faster than default password hashers
- In-memory channel layer: Avoids Redis overhead for tests
- SQLite: Uses in-memory SQLite database for faster tests
"""

import os

# Import from CI settings if running in CI (has env vars set), otherwise use base with defaults
if os.environ.get("CI"):
    from role_play.settings.ci import *
else:
    from role_play.settings.base import *

    # Test-specific settings that don't require environment variables (local only)
    SECRET_KEY = "test-secret-key-not-for-production"

    DEBUG = True

    ALLOWED_HOSTS = []  # type: ignore[misc]

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

    # Email backend
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Override database to use SQLite for faster tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Use a faster password hasher for tests
# MD5 is insecure for production but perfectly fine for testing
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Use in-memory channel layer for tests (faster than Redis)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

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
