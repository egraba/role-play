import logging

import anthropic

logger = logging.getLogger(__name__)


class TextGenerator:
    """
    Class for generating text using the anthropic API.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.client = anthropic.Anthropic()
            cls.model = "claude-3-5-sonnet-20241022"
        return cls._instance

    def enrich_quest(self, prompt: str) -> str:
        """
        Enrich a quest environment based on the given prompt.
        Returns the enriched text, or the original prompt if the API call fails.
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system="You are a role play dungeon master.",
                messages=[
                    {
                        "role": "user",
                        "content": f"{prompt}",
                    }
                ],
            )
            return response.content[0].text
        except anthropic.APIStatusError as e:
            logger.warning("Anthropic API error: %s. Using original prompt.", e)
            return prompt
