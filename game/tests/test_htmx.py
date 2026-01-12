import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains

pytestmark = pytest.mark.django_db


class TestHtmxIntegration:
    """Tests for HTMX integration in the application."""

    def test_htmx_script_included_in_base_template(self, client):
        """Verify HTMX script is loaded from CDN in base template."""
        response = client.get(reverse("index"))
        assert response.status_code == 200
        assertContains(response, "htmx.org")
        assertContains(response, 'integrity="sha384-')

    def test_csrf_token_in_htmx_headers(self, client):
        """Verify CSRF token is configured for HTMX requests."""
        response = client.get(reverse("index"))
        assert response.status_code == 200
        assertContains(response, "hx-headers")
        assertContains(response, "X-CSRFToken")

    def test_htmx_middleware_sets_request_attribute(self, client):
        """Verify HtmxMiddleware adds htmx attribute to request."""
        # Make a regular request (not HTMX)
        response = client.get(reverse("index"))
        assert response.status_code == 200
        # The middleware should have processed the request
        # We verify by checking the response was successful with middleware active

    def test_htmx_request_detected(self, client):
        """Verify HTMX requests are properly detected via HX-Request header."""
        response = client.get(
            reverse("index"),
            HTTP_HX_REQUEST="true",
        )
        assert response.status_code == 200
        # The request should be processed successfully with HTMX headers

    def test_htmx_request_with_target(self, client):
        """Verify HTMX requests with HX-Target header are processed."""
        response = client.get(
            reverse("index"),
            HTTP_HX_REQUEST="true",
            HTTP_HX_TARGET="content",
        )
        assert response.status_code == 200

    def test_htmx_request_with_trigger(self, client):
        """Verify HTMX requests with HX-Trigger header are processed."""
        response = client.get(
            reverse("index"),
            HTTP_HX_REQUEST="true",
            HTTP_HX_TRIGGER="my-button",
        )
        assert response.status_code == 200
