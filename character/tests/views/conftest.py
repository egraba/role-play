import pytest

from utils.testing.factories import CharacterFactory


@pytest.fixture(scope="class")
def setup_characters(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        number_of_characters = 22
        for _ in range(number_of_characters):
            CharacterFactory()
