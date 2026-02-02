"""
Root conftest.py for pytest.

This file ensures fixtures are loaded for all tests across all apps.
The django_db_setup fixture loads required fixtures once per test session/worker.

When using pytest-xdist for parallel testing, each worker gets its own
database and session, so fixtures are loaded once per worker.
"""

import pytest
from django.core.management import call_command
from django.core.management.commands import loaddata


# List of fixtures to load in order (dependencies first)
FIXTURES = [
    "character/fixtures/advancement.yaml",
    "character/fixtures/abilities.yaml",
    "character/fixtures/languages.yaml",
    "character/fixtures/classes.yaml",
    "character/fixtures/class_features.yaml",
    "character/fixtures/skills.yaml",
    "character/fixtures/equipment.yaml",
    "character/fixtures/species_traits.yaml",
    "character/fixtures/species.yaml",
    "character/fixtures/feats.yaml",
    "character/fixtures/magic_items.yaml",
    "character/fixtures/monsters.yaml",
]


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Load fixtures for all tests.

    This fixture extends pytest-django's django_db_setup to load
    application fixtures. With pytest-xdist, each worker has its own
    session and database, so this runs once per worker.
    """
    with django_db_blocker.unblock():
        for fixture in FIXTURES:
            call_command(loaddata.Command(), fixture, verbosity=0)
