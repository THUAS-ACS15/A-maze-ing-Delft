import os
from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

Provider = Literal["ollama", "groq", "gemini", "openai"]

def langchain(provider: Provider, model_name: str | None = None) -> BaseChatModel | None:
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
        print(f"\n[Warning] Failed to load provider '{provider}': {e}")
        return None