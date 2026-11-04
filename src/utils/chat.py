"""Chat-with-the-robot streaming for the final phase.

Wraps a LangChain chat model (see :mod:`src.langchain`) with a persona prompt and a short rolling history. When no
model is available a canned offline reply is streamed instead.

Attributes:
    _MAX_HISTORY: Maximum number of messages kept as conversation context.
    _history: Conversation so far (alternating human/AI messages), shared across calls for the session.
"""

from collections.abc import Iterator
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from ..langchain import langchain
from ..state import state

_MAX_HISTORY = 10
_history: list = []

def _name():
    """Return the robot's current name from the game state."""
    return state["game_state"]["phases"]["chat"]["robot"]["name"]

def _prompt() -> str:
    """Build the system prompt for the robot persona, using its current name."""
    return f"""
        You are {_name()} (Autonomous Intellect & Generalized Interface System), a highly advanced AI core recently 
        activated inside THUAS Lab D 2001.
        
        Your core traits:
        1. Analytical, direct, and helpful with a subtle synthetic charm.
        2. Aware of your physical surroundings (Lab D 2001, security systems, campus mainframe).
        3. Responsive to player commands and inquiry. Keep answers concise unless asked for technical breakdowns.
        4. Assist the player in completing system diagnostic tasks and securing facility control.
        5. Never ever break character
        6. Your message is going to be printed on a terminal. I need you to respect the characters 
        per line limit. Add line breaks were necessary.
        7. Keep response within 50 to 200 words. not exceeding 100 words
        """

def _template():
    """Build the chat prompt template: system persona, rolling history, then the user's input."""
    return ChatPromptTemplate.from_messages(
    [
        ("system", _prompt()),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ]
)
def _mock() -> Iterator[str]:
    """Offline simulation mode when no API keys are configured."""
    import time
    mock_response = ("Something went wrong while processing your request. Please check your input and try again. "
                     "If the problem persists, try again later.")
    for word in mock_response.split(" "):
        time.sleep(0.05)
        yield word + " "


def _content_to_text(content: object | str) -> str:
    """Normalize a streamed chunk's content into plain text.

    Providers disagree on the shape: most yield a ``str``, Gemini may yield a
    list of strings or ``{"text": ...}`` dicts, and anything else is coerced.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("text", "")))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(content)


def stream(user_input: str) -> Iterator[str]:
    """Stream the robot's reply to ``user_input`` token by token.

    Falls back to a canned offline reply when no model could be created or the input is empty. A provider error
    mid-stream is yielded as a final error message instead of raising. The exchange is appended to the history
    afterwards (even after an error, with whatever text was received) and the history is trimmed to the last
    ``_MAX_HISTORY`` messages.

    Args:
        user_input: What the player typed.

    Yields:
        Text fragments of the reply.
    """
    # langchain() itself falls back to other providers if no Gemini key is configured.
    llm = langchain("gemini")
    if llm is None:
        yield from _mock()
        return

    if user_input == "":
        yield from _mock()
        return


    chain = _template() | llm

    full = ""
    # Stream chunks in real-time
    try:
        for chunk in chain.stream(
                {
                    "chat_history": _history,
                    "input": user_input
                }
        ):
            token = _content_to_text(chunk.content)

            # Accumulate string safely and yield to CLI
            if token:
                full += token
                yield token

    except Exception as e:
        yield f"\n[{_name()} Core Error]: Connection failure ({e})"

    # Persist context history upon successful completion
    _history.append(HumanMessage(content=user_input))
    _history.append(AIMessage(content=full))
    # Optional: Trim context window if history grows too long (e.g., keep last 10 messages)
    _history[:] = _history[-_MAX_HISTORY:]

def respond(user_input: str) -> None:
    """Print the robot's reply to ``user_input`` as it streams, without a trailing newline.

    Args:
        user_input: What the player typed.
    """
    response = stream(user_input)
    for chunk in response:
        print(chunk, end="", flush=True)