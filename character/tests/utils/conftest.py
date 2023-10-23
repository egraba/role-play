import pytest
from django.core.management import call_command
from django.core.management.commands import loaddata


@pytest.fixture(scope="module")
def equipment(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command(loaddata.Command(), "character/fixtures/equipment.yaml")
