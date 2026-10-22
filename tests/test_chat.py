import time
from types import SimpleNamespace

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


class _FakeChain:
    def __init__(self, chunks, error=None):
        self._chunks = chunks
        self._error = error

    def stream(self, inputs):
        if self._error is not None:
            raise self._error
        yield from self._chunks


class _FakeTemplate:
    def __init__(self, chain):
        self._chain = chain

    def __or__(self, llm):
        return self._chain


def test_stream_yields_tokens_and_persists_history(monkeypatch):
    monkeypatch.setattr(chat, "_history", [])
    chain = _FakeChain(
        [SimpleNamespace(content="Hello "), SimpleNamespace(content="world")]
    )
    monkeypatch.setattr(chat, "_template", lambda: _FakeTemplate(chain))
    monkeypatch.setattr(chat, "langchain", lambda provider: "fake-llm")

    result = list(chat.stream("hello"))

    assert result == ["Hello ", "world"]
    assert len(chat._history) == 2
    assert isinstance(chat._history[0], chat.HumanMessage)
    assert chat._history[0].content == "hello"
    assert isinstance(chat._history[1], chat.AIMessage)
    assert chat._history[1].content == "Hello world"


def test_stream_connection_error(monkeypatch, robot_state):
    monkeypatch.setattr(chat, "_history", [])
    monkeypatch.setattr(chat, "state", robot_state)
    chain = _FakeChain([], error=RuntimeError("boom"))
    monkeypatch.setattr(chat, "_template", lambda: _FakeTemplate(chain))
    monkeypatch.setattr(chat, "langchain", lambda provider: "fake-llm")

    result = list(chat.stream("hello"))

    assert result == ["\n[TESTBOT Core Error]: Connection failure (boom)"]
    assert len(chat._history) == 2
    assert chat._history[0].content == "hello"
    assert chat._history[1].content == ""


def test_stream_skips_empty_tokens(monkeypatch):
    monkeypatch.setattr(chat, "_history", [])
    chain = _FakeChain(
        [
            SimpleNamespace(content="Hello "),
            SimpleNamespace(content=""),
            SimpleNamespace(content="world"),
        ]
    )
    monkeypatch.setattr(chat, "_template", lambda: _FakeTemplate(chain))
    monkeypatch.setattr(chat, "langchain", lambda provider: "fake-llm")

    result = list(chat.stream("hello"))

    assert result == ["Hello ", "world"]
    assert chat._history[1].content == "Hello world"


def test_stream_trims_history(monkeypatch):
    monkeypatch.setattr(
        chat,
        "_history",
        [chat.HumanMessage(content=f"old {i}") for i in range(20)],
    )
    chain = _FakeChain([SimpleNamespace(content="hi")])
    monkeypatch.setattr(chat, "_template", lambda: _FakeTemplate(chain))
    monkeypatch.setattr(chat, "langchain", lambda provider: "fake-llm")

    list(chat.stream("hello"))

    assert len(chat._history) == chat._MAX_HISTORY
    assert chat._history[-2].content == "hello"
    assert chat._history[-1].content == "hi"
