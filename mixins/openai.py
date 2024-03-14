import os
from openai import OpenAI


class OpenAIMixin:
    def initialize_openai(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.openai_api_key)