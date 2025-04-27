import logging
import time
from functools import lru_cache
from typing import Optional, List

import anthropic
from openai import OpenAI

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
        """
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


class ImageGenerator:
    """
    Class for generating images using the OpenAI API.

    This class is implemented as a singleton and provides methods to generate
    character portraits using the DALL-E API with caching and error handling.
    """

    _instance = None
    _cache: dict[str, str] = {}

    # Maximum number of retries for API calls
    MAX_RETRIES = 3
    # Delay between retries in seconds
    RETRY_DELAY = 2

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.client = OpenAI()
            cls.model = "dall-e-3"
            cls._cache = {}
        return cls._instance

    def _create_portrait_prompt(
        self, race: str, klass: str, background: str, gender: Optional[str] = None
    ) -> str:
        """
        Create a detailed prompt for character portrait generation.

        Args:
            race: Character race (e.g., Human, Elf, Dwarf)
            klass: Character class (e.g., Wizard, Fighter, Cleric)
            background: Character background (e.g., Soldier, Noble, Sage)
            gender: Optional gender specification

        Returns:
            A detailed prompt string for the image generation API
        """
        gender_text = f"{gender} " if gender else ""

        prompt = f"""Create a high-quality fantasy portrait of a {gender_text}{race} {klass} with a {background} background.

        Style: Detailed fantasy illustration, professional character portrait
        View: Chest-up portrait, facing slightly to the side
        Background: Simple, thematic to the character's background
        Lighting: Dramatic fantasy lighting
        Details: Include elements that show the character's class and background
        Important: NO TEXT or watermarks in the image
        """

        return prompt

    @lru_cache(maxsize=32)
    def generate(self, prompt: str) -> str:
        """
        Generate an image based on the given prompt.
        Uses caching to avoid duplicate API calls for the same prompt.

        Args:
            prompt: The text prompt for image generation

        Returns:
            The URL of the generated image

        Raises:
            Exception: If image generation fails after retries
        """
        # Check cache first
        if prompt in self._cache:
            logger.info(f"Using cached image for prompt: {prompt[:50]}...")
            return self._cache[prompt]

        # API call with retries
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.client.images.generate(
                    model=self.model,
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                image_url = response.data[0].url

                # Cache the result
                self._cache[prompt] = image_url
                return image_url

            except Exception as e:
                logger.error(
                    f"Error generating image (attempt {attempt + 1}): {str(e)}"
                )
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                else:
                    raise Exception(
                        f"Failed to generate image after {self.MAX_RETRIES} attempts: {str(e)}"
                    )
        # This line should never be reached, but mypy requires it
        return ""

    def generate_character_portraits(
        self,
        race: str,
        klass: str,
        background: str,
        gender: Optional[str] = None,
        count: int = 3,
    ) -> List[str]:
        """
        Generate multiple character portraits based on character attributes.

        Args:
            race: Character race
            klass: Character class
            background: Character background
            gender: Optional character gender
            count: Number of portraits to generate

        Returns:
            List of image URLs
        """
        prompt = self._create_portrait_prompt(race, klass, background, gender)
        result = []

        for i in range(count):
            try:
                # Add a small variation to the prompt to get different images
                variant_prompt = f"{prompt}\nVariation #{i + 1}: Make this unique from other variations."
                url = self.generate(variant_prompt)
                result.append(url)
            except Exception as e:
                logger.error(f"Failed to generate portrait {i + 1}: {str(e)}")
                # Continue with other generations even if one fails

        return result
