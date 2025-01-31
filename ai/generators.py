import anthropic
from openai import OpenAI


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
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.client = OpenAI()
            cls.model = ("dall-e-3",)
        return cls._instance

    def generate(self, prompt: str) -> str:
        """
        Generate an image based on the given prompt.
        Returns the URL of the generated image.
        """
        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
