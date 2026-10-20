import os

from .display_functional import out
from .state_functional import state

client = ""
provider = "google"

def init(mock: bool = False) -> None:
    if mock is False:
        return None

    try:
        from google import genai  # type: ignore[import-not-found]
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        provider = "google"
    except ImportError:
        try:
            import openai  # type: ignore[import-not-found]
            client = openai.OpenAI(api_key=os.getenv(
            "OPENAI_API_KEY"
            ))
            provider = "openai"
        except ModuleNotFoundError:
            out(
                "[!] Warning: Neither google-genai nor openai Python package installed. Defaulting to mock mode."
            )