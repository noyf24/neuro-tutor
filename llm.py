from google import genai
from google.genai import types
import os

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL_NAME = "gemini-2.5-flash"

def generate_text(prompt):

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3
        )
    )

    return response.text