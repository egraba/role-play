import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from character.views.character import CharacterSelectPortraitView
from character.tests.factories import CharacterFactory
from user.tests.factories import UserFactory


@pytest.mark.django_db
class TestCharacterSelectPortraitView:
    """Test the character portrait selection view."""

    @pytest.fixture(autouse=True)
    def setup(self, client):
        """Set up a test user and character."""
        self.user = UserFactory()
        self.character = CharacterFactory(user=self.user)
        self.url = reverse("character-select-portrait", args=[self.character.pk])
        client.force_login(self.user)

    @patch("ai.generators.ImageGenerator.generate")
    def test_view_mapping(self, mock_generate, client):
        """Test that the URL maps to the correct view."""
        # Mock the image generator to return a test URL
        mock_generate.return_value = "https://example.com/test-image.jpg"

        response = client.get(self.url)
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == CharacterSelectPortraitView

    @patch("ai.generators.ImageGenerator.generate")
    def test_template_mapping(self, mock_generate, client):
        """Test that the view uses the correct template."""
        # Mock the image generator to return a test URL
        mock_generate.return_value = "https://example.com/test-image.jpg"

        response = client.get(self.url)
        assert response.status_code == 200
        assertTemplateUsed(response, "character/portraits.html")

    @patch("ai.generators.ImageGenerator.generate")
    def test_portrait_selection(self, mock_generate, client):
        """Test that selecting a portrait updates the character and redirects."""
        # Mock the image generator to return a test URL
        mock_generate.return_value = "https://example.com/test-image.jpg"

        # First get the form
        response = client.get(self.url)
        assert response.status_code == 200

        # Now submit the form with a selected portrait
        with patch("requests.get") as mock_requests_get:
            # Mock the response from downloading the image
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b"fake image data"
            mock_requests_get.return_value = mock_response

            # Submit the form
            response = client.post(
                self.url, {"portrait": "https://example.com/test-image.jpg"}
            )

            # Check that we redirected to the character detail page
            assertRedirects(
                response, reverse("character-detail", args=[self.character.pk])
            )

            # Refresh the character from the database
            self.character.refresh_from_db()

            # Check that the portrait field was updated
            assert self.character.portrait.name is not None
