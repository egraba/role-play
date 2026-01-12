"""
Integration tests to verify Django and Celery start up correctly.

These tests validate that:
- Django app configuration is valid
- Django system checks pass
- Celery app is configured and discovers tasks
- All expected Celery tasks are registered
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


class TestCeleryStartup:
    """Test Celery application startup and task registration."""

    def test_celery_app_configured(self):
        """Verify Celery app is properly configured."""
        from role_play.celery import app

        assert app is not None
        assert app.main == "role_play"

    def test_celery_broker_url_configured(self):
        """Verify Celery broker URL is configured in settings."""
        from django.conf import settings

        # Broker URL should be configured for Redis
        assert hasattr(settings, "CELERY_BROKER_URL")
        assert "redis" in settings.CELERY_BROKER_URL

    def test_celery_tasks_autodiscovered(self):
        """Verify Celery autodiscovers tasks from Django apps."""
        # Import the tasks module to trigger task registration
        import game.tasks  # noqa: F401

        from role_play.celery import app

        # Get all registered tasks (excluding built-in celery tasks)
        registered_tasks = [
            name for name in app.tasks.keys() if not name.startswith("celery.")
        ]

        assert len(registered_tasks) > 0, "No application tasks were registered"

    def test_expected_game_tasks_registered(self):
        """Verify all expected game tasks are registered."""
        # Import the tasks module to trigger task registration
        import game.tasks  # noqa: F401

        from role_play.celery import app

        expected_tasks = [
            "game.tasks.process_roll",
            "game.tasks.store_message",
            "game.tasks.send_mail",
            "game.tasks.process_combat_initiative_roll",
        ]

        registered_tasks = list(app.tasks.keys())

        for task_name in expected_tasks:
            assert task_name in registered_tasks, f"Task '{task_name}' not registered"

    def test_task_can_be_imported_and_called(self, mocker):
        """Verify a simple task can be invoked."""
        from game.tasks import send_mail

        mock_send = mocker.patch("game.tasks.django_send_mail")

        # Call the task directly (not through Celery)
        send_mail(
            subject="Test Subject",
            message="Test Message",
            from_email="test@example.com",
            recipient_list=["recipient@example.com"],
        )

        mock_send.assert_called_once_with(
            "Test Subject",
            "Test Message",
            "test@example.com",
            ["recipient@example.com"],
        )
