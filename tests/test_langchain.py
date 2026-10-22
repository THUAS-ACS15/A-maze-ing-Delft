"""Tests for the provider factory in ``src/langchain.py``."""

from unittest.mock import Mock

import pytest

import src.langchain as langchain_module


@pytest.mark.parametrize(
    ("model_name", "expected_model"),
    [
        pytest.param(None, "llama3.2:3b", id="default-model"),
        pytest.param("custom-ollama", "custom-ollama", id="custom-model"),
    ],
)
def test_ollama(monkeypatch, model_name, expected_model):
    fake = Mock(return_value="ollama-instance")
    monkeypatch.setattr(langchain_module, "ChatOllama", fake)

    result = langchain_module.langchain("ollama", model_name)

    assert result == "ollama-instance"
    fake.assert_called_once_with(model=expected_model)


@pytest.mark.parametrize(
    ("provider", "env_var", "factory_attr", "model_name", "expected_model"),
    [
        pytest.param(
            "groq", "GROQ_API_KEY", "ChatGroq", None,
            "openai/gpt-oss-120b", id="groq-default",
        ),
        pytest.param(
            "groq", "GROQ_API_KEY", "ChatGroq", "custom-groq",
            "custom-groq", id="groq-custom",
        ),
        pytest.param(
            "gemini", "GEMINI_API_KEY", "ChatGoogleGenerativeAI", None,
            "models/gemini-3.5-flash-lite", id="gemini-default",
        ),
        pytest.param(
            "gemini", "GEMINI_API_KEY", "ChatGoogleGenerativeAI", "custom-gemini",
            "custom-gemini", id="gemini-custom",
        ),
        pytest.param(
            "openai", "OPENAI_API_KEY", "ChatOpenAI", None,
            "gpt-4o-mini", id="openai-default",
        ),
        pytest.param(
            "openai", "OPENAI_API_KEY", "ChatOpenAI", "custom-openai",
            "custom-openai", id="openai-custom",
        ),
    ],
)
def test_hosted_provider_with_key(
    monkeypatch, provider, env_var, factory_attr, model_name, expected_model
):
    monkeypatch.setenv(env_var, "secret")
    fake = Mock(return_value=f"{provider}-instance")
    monkeypatch.setattr(langchain_module, factory_attr, fake)

    result = langchain_module.langchain(provider, model_name)

    assert result == f"{provider}-instance"
    fake.assert_called_once_with(model=expected_model, streaming=True)


@pytest.mark.parametrize(
    ("provider", "env_var", "factory_attr"),
    [
        pytest.param("groq", "GROQ_API_KEY", "ChatGroq", id="groq"),
        pytest.param("gemini", "GEMINI_API_KEY", "ChatGoogleGenerativeAI", id="gemini"),
        pytest.param("openai", "OPENAI_API_KEY", "ChatOpenAI", id="openai"),
    ],
)
def test_hosted_provider_requires_api_key(monkeypatch, provider, env_var, factory_attr):
    monkeypatch.delenv(env_var, raising=False)
    ollama_fake = Mock(return_value="fallback-ollama")
    target_fake = Mock()
    monkeypatch.setattr(langchain_module, "ChatOllama", ollama_fake)
    monkeypatch.setattr(langchain_module, factory_attr, target_fake)

    result = langchain_module.langchain(provider)

    assert result == "fallback-ollama"
    target_fake.assert_not_called()


def test_fallback_prefers_ollama(monkeypatch):
    ollama_fake = Mock(return_value="ollama")
    gemini_fake = Mock()
    openai_fake = Mock()
    groq_fake = Mock()
    monkeypatch.setattr(langchain_module, "ChatOllama", ollama_fake)
    monkeypatch.setattr(langchain_module, "ChatGoogleGenerativeAI", gemini_fake)
    monkeypatch.setattr(langchain_module, "ChatOpenAI", openai_fake)
    monkeypatch.setattr(langchain_module, "ChatGroq", groq_fake)

    # "unknown" matches no provider branch, forcing the fallback chain.
    assert langchain_module.langchain("unknown") == "ollama"
    gemini_fake.assert_not_called()
    openai_fake.assert_not_called()
    groq_fake.assert_not_called()


def test_fallback_uses_gemini_when_ollama_fails(monkeypatch):
    monkeypatch.setattr(
        langchain_module, "ChatOllama", Mock(side_effect=RuntimeError("no ollama"))
    )
    gemini_fake = Mock(return_value="gemini")
    openai_fake = Mock()
    groq_fake = Mock()
    monkeypatch.setattr(langchain_module, "ChatGoogleGenerativeAI", gemini_fake)
    monkeypatch.setattr(langchain_module, "ChatOpenAI", openai_fake)
    monkeypatch.setattr(langchain_module, "ChatGroq", groq_fake)

    assert langchain_module.langchain("unknown") == "gemini"
    gemini_fake.assert_called_once()
    openai_fake.assert_not_called()
    groq_fake.assert_not_called()


def test_fallback_uses_openai_when_ollama_and_gemini_fail(monkeypatch):
    monkeypatch.setattr(
        langchain_module, "ChatOllama", Mock(side_effect=RuntimeError("no ollama"))
    )
    monkeypatch.setattr(
        langchain_module,
        "ChatGoogleGenerativeAI",
        Mock(side_effect=RuntimeError("no gemini")),
    )
    openai_fake = Mock(return_value="openai")
    groq_fake = Mock()
    monkeypatch.setattr(langchain_module, "ChatOpenAI", openai_fake)
    monkeypatch.setattr(langchain_module, "ChatGroq", groq_fake)

    assert langchain_module.langchain("unknown") == "openai"
    openai_fake.assert_called_once()
    groq_fake.assert_not_called()


def test_fallback_uses_groq_when_all_fail(monkeypatch):
    monkeypatch.setattr(
        langchain_module, "ChatOllama", Mock(side_effect=RuntimeError("no ollama"))
    )
    monkeypatch.setattr(
        langchain_module,
        "ChatGoogleGenerativeAI",
        Mock(side_effect=RuntimeError("no gemini")),
    )
    monkeypatch.setattr(
        langchain_module, "ChatOpenAI", Mock(side_effect=RuntimeError("no openai"))
    )
    groq_fake = Mock(return_value="groq")
    monkeypatch.setattr(langchain_module, "ChatGroq", groq_fake)

    assert langchain_module.langchain("unknown") == "groq"
    groq_fake.assert_called_once()


@pytest.mark.parametrize(
    ("provider", "env_var", "factory_attr"),
    [
        pytest.param("ollama", None, "ChatOllama", id="ollama"),
        pytest.param("groq", "GROQ_API_KEY", "ChatGroq", id="groq"),
        pytest.param("gemini", "GEMINI_API_KEY", "ChatGoogleGenerativeAI", id="gemini"),
        pytest.param("openai", "OPENAI_API_KEY", "ChatOpenAI", id="openai"),
    ],
)
def test_provider_constructor_error_returns_none(
    monkeypatch, capsys, provider, env_var, factory_attr
):
    if env_var is not None:
        monkeypatch.setenv(env_var, "secret")
    monkeypatch.setattr(
        langchain_module, factory_attr, Mock(side_effect=RuntimeError("boom"))
    )

    result = langchain_module.langchain(provider)

    assert result is None
    assert f"Failed to load provider '{provider}'" in capsys.readouterr().out
