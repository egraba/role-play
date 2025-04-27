import pytest
from unittest.mock import patch, MagicMock

from ai.generators import TextGenerator, ImageGenerator


def test_text_generator_singleton_instance():
    """Test that TextGenerator is a singleton."""
    instance1 = TextGenerator()
    instance2 = TextGenerator()
    assert instance1 is instance2


def test_image_generator_singleton_instance():
    """Test that ImageGenerator is a singleton."""
    instance1 = ImageGenerator()
    instance2 = ImageGenerator()
    assert instance1 is instance2


def test_image_generator_model():
    """Test that the model property is correct."""
    generator = ImageGenerator()
    assert generator.model == "dall-e-3"


def test_create_portrait_prompt():
    """Test the portrait prompt generation."""
    generator = ImageGenerator()

    # Test with gender
    prompt1 = generator._create_portrait_prompt("Elf", "Wizard", "Sage", "Female")
    assert "Female Elf Wizard" in prompt1
    assert "Sage background" in prompt1

    # Test without gender
    prompt2 = generator._create_portrait_prompt("Dwarf", "Fighter", "Soldier")
    assert "Dwarf Fighter" in prompt2
    assert "Soldier background" in prompt2
    assert "Female" not in prompt2


@patch("ai.generators.ImageGenerator.generate")
def test_generate_character_portraits(mock_generate):
    """Test generating multiple character portraits."""
    # Setup mock
    mock_generate.side_effect = ["url1", "url2", "url3"]

    # Call the method
    generator = ImageGenerator()
    urls = generator.generate_character_portraits(
        race="Elf", klass="Wizard", background="Sage", gender="Female", count=3
    )

    # Assertions
    assert len(urls) == 3
    assert urls == ["url1", "url2", "url3"]
    assert mock_generate.call_count == 3


class TestImageGeneratorWithMocks:
    """Tests that mock the OpenAI API calls completely."""

    @pytest.fixture
    def mock_openai_client(self):
        """Create a mocked OpenAI client."""
        with patch("ai.generators.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def fresh_generator(self, mock_openai_client):
        """Create a fresh image generator with a mocked client."""
        # Reset the singleton
        ImageGenerator._instance = None
        generator = ImageGenerator()
        # Replace the client with our mock
        generator.client = mock_openai_client
        # Clear the cache
        generator._cache = {}
        return generator

    def test_caching(self, fresh_generator, mock_openai_client):
        """Test that generate() uses caching."""
        # Setup response
        mock_response = MagicMock()
        mock_response.data = [MagicMock(url="test_url")]
        mock_openai_client.images.generate.return_value = mock_response

        # First call should use the API
        url1 = fresh_generator.generate("test prompt")
        assert url1 == "test_url"
        mock_openai_client.images.generate.assert_called_once()

        # Reset the mock
        mock_openai_client.images.generate.reset_mock()

        # Second call should use the cache
        url2 = fresh_generator.generate("test prompt")
        assert url2 == "test_url"
        mock_openai_client.images.generate.assert_not_called()

    def test_retry_on_error(self, fresh_generator, mock_openai_client):
        """Test that generate() retries on error."""
        # Setup responses
        mock_response = MagicMock()
        mock_response.data = [MagicMock(url="test_url")]
        mock_openai_client.images.generate.side_effect = [
            Exception("API Error"),  # First call fails
            mock_response,  # Second call succeeds
        ]

        # Call should retry and succeed
        with patch("ai.generators.time.sleep") as mock_sleep:
            url = fresh_generator.generate("test prompt")
            assert url == "test_url"
            assert mock_openai_client.images.generate.call_count == 2
            mock_sleep.assert_called_once()

    def test_max_retries_exceeded(self, fresh_generator, mock_openai_client):
        """Test that generate() raises after max retries."""
        # Always raise an exception
        mock_openai_client.images.generate.side_effect = Exception("API Error")

        # Set a small retry count
        fresh_generator.MAX_RETRIES = 2

        # Should retry and fail
        with patch("ai.generators.time.sleep") as mock_sleep:
            with pytest.raises(Exception) as excinfo:
                fresh_generator.generate("test prompt")

            assert "Failed to generate image after 2 attempts" in str(excinfo.value)
            assert mock_openai_client.images.generate.call_count == 2
            assert mock_sleep.call_count == 1  # Called once between retries
