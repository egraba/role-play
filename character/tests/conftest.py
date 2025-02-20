import pytest
from django.core.management import call_command
from django.core.management.commands import loaddata
from .factories import CharacterFactory


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command(loaddata.Command(), "character/fixtures/senses.yaml")
        call_command(loaddata.Command(), "character/fixtures/advancement.yaml")
        call_command(loaddata.Command(), "character/fixtures/abilities.yaml")
        call_command(loaddata.Command(), "character/fixtures/languages.yaml")
        call_command(loaddata.Command(), "character/fixtures/klasses.yaml")
        call_command(loaddata.Command(), "character/fixtures/skills.yaml")
        call_command(loaddata.Command(), "character/fixtures/equipment.yaml")


@pytest.fixture(scope="function")
def character():
    return CharacterFactory()
