import pytest
from django.test import override_settings
from django.urls import reverse

from .factories import UserWithPasswordFactory

pytestmark = pytest.mark.django_db


@override_settings(
    RATELIMIT_ENABLE=True,
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
def test_login_blocked_after_five_failed_attempts(client):
    UserWithPasswordFactory(username="target")
    login_url = reverse("login")

    for _ in range(5):
        client.post(login_url, {"username": "target", "password": "wrong"})

    response = client.post(login_url, {"username": "target", "password": "wrong"})
    assert response.status_code == 403
