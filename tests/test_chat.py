import time

import pytest

from src.utils import chat

MOCK_MESSAGE = (
    "Something went wrong while processing your request. "
    "Please check your input and try again. "
    "If the problem persists, try again later."
)


@pytest.fixture(autouse=True)
def _fast_sleep(monkeypatch):
    """mock() sleeps 0.05s per word; patch it out so tests stay fast."""
    monkeypatch.setattr(time, "sleep", lambda *args, **kwargs: None)


@pytest.fixture
def robot_state():
    return {
        "game_state": {
            "phases": {
                "chat": {
                    "robot": {"name": "TESTBOT"},
                }
            }
        }
    }


def test_mock_yields_expected_words():
    words = list(chat._mock())
    assert len(words) == 21
    assert all(word.endswith(" ") for word in words)
    assert "".join(words) == MOCK_MESSAGE + " "


def test_name_reads_robot_name(monkeypatch, robot_state):
    monkeypatch.setattr(chat, "state", robot_state)
    assert chat._name() == "TESTBOT"


def test_prompt_includes_name_and_lab(monkeypatch, robot_state):
    monkeypatch.setattr(chat, "state", robot_state)
    result = chat._prompt()
    assert isinstance(result, str)
    assert "You are TESTBOT" in result
    assert "THUAS Lab D 2001" in result


def test_template_returns_chat_prompt_template(monkeypatch, robot_state):
    from langchain_core.prompts import ChatPromptTemplate

    monkeypatch.setattr(chat, "state", robot_state)
    assert isinstance(chat._template(), ChatPromptTemplate)


def test_stream_falls_back_without_llm(monkeypatch):
    monkeypatch.setattr(chat, "langchain", lambda provider: None)
    assert "".join(chat.stream("hello")) == MOCK_MESSAGE + " "


def test_stream_falls_back_on_empty_input(monkeypatch):
    monkeypatch.setattr(chat, "langchain", lambda provider: object())
    assert "".join(chat.stream("")) == MOCK_MESSAGE + " "


def test_respond_prints_stream_output(capsys, monkeypatch):
    monkeypatch.setattr(chat, "langchain", lambda provider: None)
    chat.respond("hello")
    assert MOCK_MESSAGE in capsys.readouterr().out


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("hello", "hello"),
        ("", ""),
        (["hello", " ", "world"], "hello world"),
        ([{"text": "hello"}, {"text": " world"}], "hello world"),
        (["hello", {"text": " world"}], "hello world"),
        (["hello", 42], "hello42"),
        ([], ""),
        (123, "123"),
        (None, "None"),
    ],
)
def test_content_to_text_normalizes_provider_shapes(content, expected):
    assert chat._content_to_text(content) == expected
