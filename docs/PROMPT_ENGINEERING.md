# AI Integration Reference

This document describes the optional LangChain-based chat module in `utilities/chat.py` and `utilities/langchain.py`.

> **Current status:** the module is **not connected to the game**. No room, menu, or ending imports `utilities.chat` or calls `respond()`/`stream()`. The current ending is the `play_game_complete()` cutscene in `utilities/story_animations.py`. The game does not need an API key to run.

The old `src/client.py` integration and the JSON/`system_prompt.txt` approach described in earlier documentation have been removed. The current AI code is a standalone helper that can be wired into a future chat phase.

## Contents

- [Module layout](#module-layout)
- [System prompt](#system-prompt)
- [Providers and fallback order](#providers-and-fallback-order)
- [History and context window](#history-and-context-window)
- [Streaming and mock fallback](#streaming-and-mock-fallback)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Limitations](#limitations)
- [Wiring it into the game later](#wiring-it-into-the-game-later)

## Module layout

| File | Responsibility |
| --- | --- |
| `utilities/chat.py` | Builds the prompt template, keeps rolling history, streams model output, and provides a mock fallback. |
| `utilities/langchain.py` | Creates a chat model for Ollama, Groq, Gemini, or OpenAI, with fallback when a provider is unavailable. |
| `utilities/display.py` | Provides `out()` and `safe()` for cp1252-safe terminal output. |

`utilities/chat.py` exposes:

- `stream(user_input)` — generator that yields text fragments.
- `respond(user_input)` — prints the streamed reply without a trailing newline.
- `_prompt()` — the system prompt.
- `_template()` — a `ChatPromptTemplate` containing the system prompt, a `MessagesPlaceholder("chat_history")`, and the human input.

## System prompt

The current prompt is defined in `_prompt()` in `utilities/chat.py`:

```text
You are an (Autonomous Intellect & Generalized Interface System), a highly advanced AI core recently
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
```

The prompt is intentionally short. It does not include a separate guardrail message, a jailbreak-response instruction, or a structured persona document. Those were part of the removed design, not the current code.

## Providers and fallback order

`utilities/langchain.py` defines:

```python
Provider = Literal["ollama", "groq", "gemini", "openai"]
```

`langchain(provider, model_name=None)` tries to construct a model and returns `None` if every attempt fails. It never raises for a provider failure; it prints a warning through `utilities.display.out()`.

| Provider | Required environment variable | Default model | Notes |
| --- | --- | --- | --- |
| `ollama` | none | `llama3.2:3b` | Local model; needs a running Ollama instance. |
| `groq` | `GROQ_API_KEY` | `openai/gpt-oss-120b` | Hosted; streaming enabled. |
| `gemini` | `GEMINI_API_KEY` | `models/gemini-3.5-flash-lite` | Hosted; streaming enabled. |
| `openai` | `OPENAI_API_KEY` | `gpt-4o-mini` | Hosted; streaming enabled. |

If the requested provider is unrecognized or its API key is not set, the `else` branch tries this order and returns the first constructor that does not raise:

```text
Ollama -> Gemini -> OpenAI -> Groq
```

If a recognized provider's constructor itself raises, the outer exception handler prints a warning and returns `None`; it does not fall through in that case. `utilities/chat.py` calls `langchain("gemini")`, so Gemini is returned when `GEMINI_API_KEY` is set; otherwise the fallback chain applies. If none can be constructed, `stream()` uses the mock response.

## History and context window

`utilities/chat.py` keeps a module-level `_history` list and a `_MAX_HISTORY` constant:

```python
_MAX_HISTORY = 10
_history: list = []
```

After each exchange, the module appends a `HumanMessage` and an `AIMessage`, then trims the list:

```python
_history[:] = _history[-_MAX_HISTORY:]
```

The prompt template receives the history through `MessagesPlaceholder(variable_name="chat_history")`. The system prompt is part of the template, not stored in `_history`, so trimming only affects the conversation turns.

The history is process-local. It is not saved to `saves.db` and does not survive a restart.

## Streaming and mock fallback

`stream(user_input)`:

1. Creates a model with `langchain("gemini")`.
2. If the model is `None`, or the input is empty, yields the mock response.
3. Otherwise builds `_template() | llm` and iterates over `chain.stream(...)`.
4. Normalises each chunk's content with `_content_to_text()`. This handles plain strings, Gemini's list/dict content shapes, and other values.
5. Yields non-empty text fragments.
6. Catches provider errors and yields a final `[Core Error]: Connection failure (...)` message instead of raising.
7. Appends the exchange to `_history` even after an error, using whatever text was received.

The mock fallback is:

```text
Something went wrong while processing your request. Please check your input and try again.
If the problem persists, try again later.
```

It is streamed one word at a time with a short delay. `respond()` prints the streamed chunks with `end=""` and `flush=True`.

## Configuration

The hosted providers read keys from the environment. The supported key names are:

```text
GEMINI_API_KEY
GROQ_API_KEY
OPENAI_API_KEY
```

The repository's `.env` file is ignored by Git. `.env.test` currently lists `GEMINI_API_KEY` and `OPENAI_API_KEY` as placeholders; never put real values in `.env.test`. Ollama needs no key.

The current game does not load `.env` itself in `main.py`; the AI module only works if the environment already contains the key (or if the code is wired into a launcher that loads `.env`). This is another reason the module is currently optional rather than part of normal play.

## Dependencies

`utilities/chat.py` imports:

```text
langchain_core
```

`utilities/langchain.py` imports:

```text
langchain_core
langchain_ollama
langchain_google_genai
langchain_openai
langchain_groq
```

These packages are **not** listed in `requirements.txt`. `pyproject.toml` only adds mypy overrides so missing LangChain imports do not fail type checking.

If you want to use the module directly, install the extras in your environment:

```bash
python -m pip install langchain-core langchain-ollama langchain-google-genai langchain-openai langchain-groq
```

Do not add these to `requirements.txt` unless the game actually imports the module; doing so would make every install heavier for an unused feature.

## Limitations

- **Not wired:** no current game path calls `stream()` or `respond()`.
- **No CLI integration:** there is no chat prompt, exit command, or room transition for a conversation phase.
- **No prompt-injection guardrails:** the system prompt does not contain the defensive instructions described in older documentation.
- **No model parameter controls:** temperature, max tokens, and top-p are left at provider defaults.
- **No tests:** the current pytest suite does not cover `utilities/chat.py` or `utilities/langchain.py`.
- **No key loading:** `main.py` does not load `.env`; the environment must provide the keys.
- **Process-local history:** conversation history is lost when the process exits.
- **Prompt wording:** the current prompt contains grammar and line-length instructions that could be tightened before production use.

## Wiring it into the game later

A future chat phase would need, at minimum:

1. A room or ending path that imports `utilities.chat` and calls `respond()`.
2. A command to leave the chat and return to the game.
3. A decision about whether conversation history should be saved.
4. LangChain dependencies added to the install path.
5. Tests for the mock fallback, provider selection, streaming, and history trimming.

Until those changes exist, treat this document as a reference for the optional module, not as a description of the current ending.
