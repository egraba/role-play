import pytest
from faker import Faker

from game.channel_messages import format_message


@pytest.fixture
def fake():
    return Faker()


def test_format_message_from_master(fake):
    message = fake.text()
    assert format_message(message) == f"the Master said: {message}"


def test_format_message_from_player(fake):
    message = fake.text()
    sender = fake.first_name()
    assert format_message(message, sender) == f"{sender} said: {message}"
