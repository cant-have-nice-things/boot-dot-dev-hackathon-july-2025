import google.generativeai as genai
from google.generativeai import types
from PIL import Image
from io import BytesIO
import base64
import os

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate_playlist_image(self, playlist_name: str, playlist_description: str) -> bytes | None:
        """
        Generates a playlist image using Gemini.
        """
        prompt = f"Create a playlist cover for a playlist called '{playlist_name}'. The playlist is described as: '{playlist_description}'. The image should be square and visually appealing."

        response = self.model.generate_content(
            contents=prompt,
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                return part.inline_data.data
        return None
