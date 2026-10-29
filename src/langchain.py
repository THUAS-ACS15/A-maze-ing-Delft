"""
Factory for the chat language model used by the finale.

Supports a local Ollama model and the hosted Groq, Gemini and OpenAI providers. API keys are read from the
environment (``GROQ_API_KEY``, ``GEMINI_API_KEY``, ``OPENAI_API_KEY``).

Attributes:
    Provider: Literal type of the accepted provider names.
"""

import os
from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from .display import out

Provider = Literal["ollama", "groq", "gemini", "openai"]

def langchain(provider: Provider, model_name: str | None = None) -> BaseChatModel | None:
    """Build a chat model for ``provider``, falling back to other providers when it is unavailable.

    Ollama needs no key. A hosted provider is used only when its API key is set; otherwise (or for an unrecognised
    provider) the function tries Ollama, then Gemini, OpenAI and Groq, returning the first whose constructor does not
    raise.

    Args:
        provider: Preferred provider: ``"ollama"``, ``"groq"``, ``"gemini"`` or ``"openai"``.
        model_name: Model identifier to use. Defaults to a provider-specific model.

    Returns:
        A chat model, or ``None`` if construction failed. A warning is printed in that case; this function never raises.
    """
    try:
        # 1. Local Open Weights via Ollama
        if provider == "ollama":
            return ChatOllama(
                model=model_name or "llama3.2:3b",
            )

        # 2. Hosted Open Weights via Groq API
        elif provider == "groq" and os.getenv("GROQ_API_KEY"):
            return ChatGroq(
                model=model_name or "openai/gpt-oss-120b",
                streaming=True,
            )

        # 3. Google Gemini
        elif provider == "gemini" and os.getenv("GEMINI_API_KEY"):
            return ChatGoogleGenerativeAI(
                model=model_name or "models/gemini-3.5-flash-lite",
                streaming=True
            )

        # 4. OpenAI
        elif provider == "openai" and os.getenv("OPENAI_API_KEY"):
            return ChatOpenAI(
                model=model_name or "gpt-4o-mini",
                streaming=True
            )
        else:
            try:
                return ChatOllama(
                    model=model_name or "llama3.2:3b",
                )
            except Exception:
                try:
                    return ChatGoogleGenerativeAI(
                        model=model_name or "models/gemini-3.5-flash-lite",
                        streaming=True
                    )
                except Exception:
                    try:
                        return ChatOpenAI(
                            model=model_name or "gpt-4o-mini",
                            streaming=True
                        )
                    except Exception:
                        return ChatGroq(
                            model=model_name or "openai/gpt-oss-120b",
                            streaming=True,
                        )
    except Exception as e:
        out(f"\n[Warning] Failed to load provider '{provider}': {e}")
        return None