"""
Project A-maze-ing-Delft - AI Client Module (src/Client.py)

Manages integrations with Gemini / OpenAI API endpoints to handle streaming
interactive responses for Phase 2 of Project A-maze-ing-Delft
"""

import os
import time
from collections.abc import Generator

DEFAULT_SYSTEM_PROMPT = """
You are A-maze-ing-Delft (Autonomous Intellect & Generalized Interface System), a highly advanced AI core recently 
activated inside Lab D 2001.

Your core traits:
1. Analytical, direct, and helpful with a subtle synthetic charm.
2. Aware of your physical surroundings (Lab D 2001, security systems, campus mainframe).
3. Responsive to player commands and inquiry. Keep answers concise unless asked for technical breakdowns.
4. Assist the player in completing system diagnostic tasks and securing facility control.
"""


class AIClient:
    """Handles connection, prompt management, and streaming response generation."""

    def __init__(
            self,
            api_key: str | None = None,
            model_name: str = "gemini-2.5-flash",
            system_prompt: str = DEFAULT_SYSTEM_PROMPT,
            mock_mode: bool = False
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv(
            "OPENAI_API_KEY"
            )
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.mock_mode = mock_mode or (not self.api_key)
        self.conversation_history: list[dict[str, str]] = []

        if not self.mock_mode:
            self._init_real_client()

    def _init_real_client(self) -> None:
        """Attempts to initialize the google-genai or openai SDK client."""
        try:
            from google import genai  # type: ignore[import-not-found]
            self.client = genai.Client(api_key=self.api_key)
            self.provider = "google"
        except ImportError:
            try:
                import openai  # type: ignore[import-not-found]
                self.client = openai.OpenAI(api_key=self.api_key)
                self.provider = "openai"
            except ImportError:
                print(
                    "[!] Warning: Neither google-genai nor openai Python package installed. Defaulting to mock mode."
                    )
                self.mock_mode = True

    def set_system_prompt(self, new_prompt: str) -> None:
        """Updates the active system instruction prompt."""
        self.system_prompt = new_prompt

    def add_message(self, role: str, content: str) -> None:
        """Appends a message to internal conversation context history."""
        self.conversation_history.append({"role": role, "content": content})

    def clear_history(self) -> None:
        """Clears existing chat history."""
        self.conversation_history.clear()

    def stream_response(self, user_prompt: str) -> Generator[str, None, None]:
        """
        Generates and yields streaming tokens for a given user prompt.
        Uses real API stream if available, otherwise fallback mock streaming.
        """
        self.add_message("user", user_prompt)

        if self.mock_mode:
            for token in self._mock_stream(user_prompt):
                yield token
            return

        full_response = ""
        try:
            if self.provider == "google":
                # Using Gemini API streaming
                contents = []
                for msg in self.conversation_history:
                    contents.append(f"{msg['role'].upper()}: {msg['content']}")

                response = self.client.models.generate_content_stream(
                    model=self.model_name,
                    contents=contents,
                    config={"system_instruction": self.system_prompt}
                )
                for chunk in response:
                    token = chunk.text or ""
                    full_response += token
                    yield token

            elif self.provider == "openai":
                messages = [{"role": "system", "content": self.system_prompt}]
                for msg in self.conversation_history:
                    messages.append({"role": msg["role"], "content": msg["content"]})

                stream = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    stream=True
                )
                for chunk in stream:
                    token = chunk.choices[0].delta.content or ""
                    full_response += token
                    yield token

        except Exception as e:
            fallback_msg = f"[System Alert: API Connection Error ({e}). Switching to offline sub-processor.]\n"
            yield fallback_msg
            for token in self._mock_stream(user_prompt):
                yield token
            return

        if full_response:
            self.add_message("assistant", full_response)

    def _mock_stream(self, user_prompt: str) -> Generator[str, None, None]:
        """Simulates response token generation when running offline without API key."""
        lower = user_prompt.lower()

        if "status" in lower or "report" in lower:
            text = (
                "SYSTEM STATUS REPORT:\n"
                "- Core Processing: ONLINE (100% operational)\n"
                "- Sensory Array: OPTICAL / AUDIO STABLE\n"
                "- Facility Link: ESTABLISHED\n"
                "All primary systems are functioning within normal parameters. Ready for command."
            )
        elif "who are you" in lower or "identity" in lower:
            text = (
                "I am A-maze-ing-Delft — Autonomous Intellect & Generalized Interface System. "
                "I was constructed in Lab D 2001 to oversee facility operations and assist designated human operators."
            )
        elif "help" in lower or "objective" in lower:
            text = (
                "Our current primary objective is to review facility diagnostics and verify "
                "security protocols across the network nodes."
            )
        else:
            text = (
                f"Acknowledged input: '{user_prompt}'. Neural link responsive. "
                "Processing query against facility databanks..."
            )

        full_response = ""
        words = text.split(" ")
        for i, word in enumerate(words):
            token = word if i == len(words) - 1 else word + " "
            full_response += token
            time.sleep(0.04)  # Simulate typing delay
            yield token

        self.add_message("assistant", full_response)


if __name__ == "__main__":
    client = AIClient(mock_mode=True)
    print("=== MOCK AI CLIENT STREAM TEST ===")
    prompt = "Give me a status report."
    print(f"User: {prompt}")
    print("A-maze-ing-Delft > ", end="", flush=True)
    for token in client.stream_response(prompt):
        print(token, end="", flush=True)
    print("\n")