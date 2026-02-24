import pytest
from django.db.utils import OperationalError
from django.urls import reverse


@pytest.mark.django_db
def test_health_check_returns_ok(client):
    response = client.get(reverse("health_check"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_health_check_returns_503_when_db_is_unreachable(client, mocker):
    mocker.patch(
        "django.db.connection.ensure_connection",
        side_effect=OperationalError("connection refused"),
    )
    response = client.get(reverse("health_check"))
    assert response.status_code == 503
    assert response.json()["status"] == "error"
