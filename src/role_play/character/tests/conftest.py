import os

import pytest
from django.core.management import call_command
from django.core.management.commands import loaddata


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        fixtures_path = os.environ["PYTHONPATH"] + "/character/fixtures/"
        for fixture in [
            "senses",
            "advancement",
            "abilities",
            "languages",
            "klasses",
            "skills",
            "equipment",
        ]:
            call_command(loaddata.Command(), f"{fixtures_path}{fixture}.yaml")
