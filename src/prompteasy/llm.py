import os
from dotenv import load_dotenv
from groq import Groq

class GroqProvider:
    """
    Provides access to Groq-hosted language models.
    """

    def __init__(self, model:str = "openai/gpt-oss-20b"):

        load_dotenv()

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set"
                "Add it to your .env file"
            )

        self.client = Groq(api_key=api_key)
        self.model = model