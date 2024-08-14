import pytest

from user.models import User

from .factories import UserFactory

pytestmark = pytest.mark.django_db


class TestUser:
    def test_creation(self):
        user = UserFactory()
        assert isinstance(user, User)
