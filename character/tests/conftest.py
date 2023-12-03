import pytest
from django.core.management import call_command
from django.core.management.commands import loaddata

from utils.testing.factories import CharacterFactory


@pytest.fixture(scope="module")
def equipment(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command(loaddata.Command(), "character/fixtures/equipment.yaml")


@pytest.fixture(scope="class")
def setup_characters(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        number_of_characters = 22
        for _ in range(number_of_characters):
            CharacterFactory()
