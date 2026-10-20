from typing import Generator, Iterator
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from ..langchain import langchain
from ..state import state

NAME = state["phases"]["chat"]["robot"]["name"]
SYSTEM_PROMPT = f"""
You are {NAME} (Autonomous Intellect & Generalized Interface System), a highly advanced AI core recently 
activated inside THUAS Lab D 2001.

Your core traits:
1. Analytical, direct, and helpful with a subtle synthetic charm.
2. Aware of your physical surroundings (Lab D 2001, security systems, campus mainframe).
3. Responsive to player commands and inquiry. Keep answers concise unless asked for technical breakdowns.
4. Assist the player in completing system diagnostic tasks and securing facility control.
5. Never ever break character
6. Your message is going to be printed on a terminal. I need you to respect the characters per line limit. add line breaks were necessary.
7. Keep response within 50 to 200 words. not exceeding 200 words
"""
_MAX_HISTORY = 10
_history: list = []

prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

def mock(user_input: str) -> Iterator[str]:
    """Offline simulation mode when no API keys are configured."""
    import time
    mock_response = f"Simulated {NAME} core response to: '{user_input}'. Offline diagnostic mode active."
    for word in mock_response.split(" "):
        time.sleep(0.05)
        yield word + " "

def stream(user_input: str) -> Iterator[str]:
    llm = langchain("gemini")
    if llm is None:
        yield from mock(user_input)
        return

    chain = prompt_template | llm

    full = ""
    # Stream chunks in real-time
    try:
        for chunk in chain.stream(
                {
                    "chat_history": _history,
                    "input": user_input
                }
        ):
            raw_content = chunk.content
            if isinstance(raw_content, str):
                token = raw_content
            elif isinstance(raw_content, list):
                # Gemini can return list of dicts or strings
                token = "".join(
                    item if isinstance(item, str) else item.get("text", "")
                    for item in raw_content
                )
            else:
                token = str(raw_content)

                # 2. Accumulate string safely and yield to CLI
            if token:
                full += token
                yield token

    except Exception as e:
        yield f"\n[{NAME} Core Error]: Connection failure ({e})"

    # Persist context history upon successful completion
    _history.append(HumanMessage(content=user_input))
    _history.append(AIMessage(content=full))
    # Optional: Trim context window if history grows too long (e.g., keep last 10 messages)
    _history[:] = _history[-_MAX_HISTORY:]

def respond(user_input: str) -> None:
    response = stream(user_input)
    for chunk in response:
        print(chunk, end="", flush=True)