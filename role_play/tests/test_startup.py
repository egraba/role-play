"""
Integration tests to verify Django starts up correctly.

These tests validate that:
- Django app configuration is valid
- Django system checks pass
"""

import pytest
from django.core.management import call_command


class TestDjangoStartup:
    """Test Django application startup and configuration."""

    def test_django_system_checks_pass(self):
        """Verify all Django system checks pass without errors."""
        # This will raise CommandError if any checks fail
        call_command("check", verbosity=0)

    def test_django_app_configs_ready(self):
        """Verify all Django apps are properly configured."""
        from django.apps import apps

        # Get all installed app configs
        app_configs = apps.get_app_configs()
        assert len(app_configs) > 0

        # Verify our main apps are loaded
        expected_apps = ["character", "game", "master", "user"]
        loaded_app_names = [config.name for config in app_configs]

        for app_name in expected_apps:
            assert app_name in loaded_app_names, f"App '{app_name}' not loaded"

    def test_url_configuration_valid(self):
        """Verify URL configuration can be loaded without errors."""
        from django.urls import get_resolver

        resolver = get_resolver()
        # If we get here without exception, URLs are valid
        assert resolver is not None
        assert len(resolver.url_patterns) > 0

    @pytest.mark.django_db
    def test_database_connection(self):
        """Verify database connection works."""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
