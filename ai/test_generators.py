from unittest.mock import MagicMock, patch

import anthropic
import pytest

from ai.generators import TextGenerator


def test_singleton_instance():
    instance1 = TextGenerator()
    instance2 = TextGenerator()
    assert instance1 is instance2


@pytest.mark.django_db
def test_enrich_quest_api_error_returns_original_prompt():
    """Test that API errors are handled gracefully and return the original prompt."""
    generator = TextGenerator()
    original_prompt = "The heroes enter a dark cave"

    mock_response = MagicMock()
    mock_response.status_code = 402
    mock_response.request = MagicMock()

    with patch.object(
        generator.client.messages,
        "create",
        side_effect=anthropic.APIStatusError(
            message="Insufficient credits",
            response=mock_response,
            body=None,
        ),
    ):
        result = generator.enrich_quest(original_prompt)

    assert result == original_prompt
