import pytest

from .factories import CharacterFactory


@pytest.fixture(scope="function")
def character():
    return CharacterFactory()
