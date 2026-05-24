import os
from google import genai

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

MODEL = "gemini-2.5-flash"


def generate_text(prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text or ""