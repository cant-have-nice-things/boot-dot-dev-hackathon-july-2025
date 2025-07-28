import google.generativeai as genai
from google.generativeai import types
from PIL import Image
from io import BytesIO
import base64
import os
import time
from google.api_core import exceptions

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-preview-image-generation")

    def generate_playlist_image(self, playlist_name: str, playlist_description: str) -> bytes | None:
        """
        Generates a playlist image using Gemini.
        """
        prompt = f"Create a playlist cover for a playlist called '{playlist_name}'. The playlist is described as: '{playlist_description}'. The image should be square and visually appealing."

        response = self.model.generate_content(
            contents=prompt
        )

        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_bytes = part.inline_data.data
                    with Image.open(BytesIO(image_bytes)) as img:
                        # Resize if necessary and convert to JPEG
                        quality = 95
                        while True:
                            with BytesIO() as output:
                                img.save(output, format="JPEG", quality=quality)
                                data = output.getvalue()
                                if len(data) <= 256 * 1024:
                                    return data
                            quality -= 5
                            if quality < 10:
                                return None  # Could not compress enough
        return None
