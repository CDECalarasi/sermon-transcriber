import os
from openai import OpenAI


class OpenAIMixin:
    def __init__(self):
        self.client = None
        self.openai_api_key = None

    def initialize_openai(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.openai_api_key)
