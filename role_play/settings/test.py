"""
Test-specific Django settings optimized for faster test execution.

Key optimizations:
- MD5PasswordHasher: Much faster than default password hashers
- In-memory channel layer: Avoids Redis overhead for tests
"""

import os

# Import from CI settings if running in CI, otherwise from local
if os.environ.get("CI"):
    from role_play.settings.ci import *
else:
    from role_play.settings.local import *

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
