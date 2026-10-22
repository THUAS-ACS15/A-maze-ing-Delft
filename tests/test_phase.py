"""Tests for the single-prompt phase handlers in ``src/phase.py``."""

from unittest.mock import Mock

import pytest

from src import phase


@pytest.fixture
def mocks(monkeypatch):
    """Replace every dependency phase.py resolves at module level."""
    prompt = Mock(return_value="raw input")
    parse = Mock(return_value=("GO", {}))
    command = Mock()
    clear = Mock()
    render = Mock()
    header = Mock()
    out = Mock()
    respond = Mock()
    workbench = Mock()
    activate = Mock()

    monkeypatch.setattr(phase, "prompt", prompt)
    monkeypatch.setattr(phase, "parse", parse)
    monkeypatch.setattr(phase, "command", command)
    monkeypatch.setattr(phase, "clear", clear)
    monkeypatch.setattr(phase, "render", render)
    monkeypatch.setattr(phase, "header", header)
    monkeypatch.setattr(phase, "out", out)
    monkeypatch.setattr(phase, "respond", respond)
    monkeypatch.setattr(phase, "workbench", workbench)
    monkeypatch.setattr(phase, "activate", activate)
    monkeypatch.setattr(phase, "colorize", lambda text, color_code=None: text)

    state = {
        "game_state": {
            "phases": {
                "assembly": {"activated": False},
                "chat": {"activated": False, "robot": {"name": "A.I.G.I.S."}},
            }
        },
        "player": {"current_room": "lab_d2_001"},
    }
    monkeypatch.setattr(phase, "state", state)

    return {
        "prompt": prompt,
        "parse": parse,
        "command": command,
        "clear": clear,
        "render": render,
        "header": header,
        "out": out,
        "respond": respond,
        "workbench": workbench,
        "activate": activate,
        "state": state,
    }


def test_exploration_valid_verb(mocks):
    mocks["prompt"].return_value = "go north"
    mocks["parse"].return_value = ("GO", {"direction": "north"})

    phase.exploration()

    mocks["parse"].assert_called_once_with("go north")
    mocks["command"].assert_called_once_with("GO", {"direction": "north"})
    mocks["clear"].assert_called_once()
    mocks["render"].assert_not_called()


@pytest.mark.parametrize("verb", ["UNKNOWN", "INVALID", "EMPTY"])
def test_exploration_invalid_verb_renders_error(mocks, verb):
    mocks["parse"].return_value = (verb, {})

    phase.exploration()

    mocks["render"].assert_called_once()
    assert "Invalid input" in mocks["render"].call_args.args[0]


def test_assembly_first_run_shows_workbench_and_activates(mocks):
    phase.assembly()

    mocks["workbench"].assert_called_once()
    assert "Build your dream robot" in mocks["workbench"].call_args.args[0]
    mocks["clear"].assert_called_once()
    mocks["prompt"].assert_not_called()
    assert mocks["state"]["game_state"]["phases"]["assembly"]["activated"] is True


def test_assembly_activate_verb_triggers_activation(mocks):
    mocks["state"]["game_state"]["phases"]["assembly"]["activated"] = True
    mocks["parse"].return_value = ("activate", {})

    phase.assembly()

    mocks["activate"].assert_called_once()
    mocks["render"].assert_not_called()


@pytest.mark.parametrize("verb", ["UNKNOWN", "INVALID", "EMPTY"])
def test_assembly_invalid_verb_renders_error(mocks, verb):
    mocks["state"]["game_state"]["phases"]["assembly"]["activated"] = True
    mocks["parse"].return_value = (verb, {})

    phase.assembly()

    mocks["render"].assert_called_once()
    assert "Invalid input" in mocks["render"].call_args.args[0]
    mocks["activate"].assert_not_called()


def test_chat_first_run_renders_welcome_and_activates(mocks):
    phase.chat()

    mocks["render"].assert_called_once()
    welcome = mocks["render"].call_args.args[0]
    assert "Welcome" in welcome
    assert "A.I.G.I.S." in welcome
    assert mocks["state"]["game_state"]["phases"]["chat"]["activated"] is True
    mocks["prompt"].assert_not_called()


@pytest.mark.parametrize("verb", ["UNKNOWN", "INVALID", "EMPTY"])
def test_chat_invalid_verb_in_lab_responds(mocks, verb):
    mocks["state"]["game_state"]["phases"]["chat"]["activated"] = True
    mocks["state"]["player"]["current_room"] = "lab_d2_001"
    mocks["prompt"].return_value = "hello robot"
    mocks["parse"].return_value = (verb, {})

    phase.chat()

    mocks["header"].assert_called_once()
    mocks["respond"].assert_called_once_with("hello robot")
    mocks["render"].assert_not_called()


@pytest.mark.parametrize("verb", ["UNKNOWN", "INVALID", "EMPTY"])
def test_chat_invalid_verb_not_in_lab_renders_error(mocks, verb):
    mocks["state"]["game_state"]["phases"]["chat"]["activated"] = True
    mocks["state"]["player"]["current_room"] = "teachers_room_1"
    mocks["parse"].return_value = (verb, {})

    phase.chat()

    mocks["render"].assert_called_once()
    assert "Invalid input" in mocks["render"].call_args.args[0]
    mocks["respond"].assert_not_called()
    mocks["header"].assert_not_called()


def test_chat_valid_verb_runs_command_only(mocks):
    mocks["state"]["game_state"]["phases"]["chat"]["activated"] = True
    mocks["parse"].return_value = ("SAY", {"message": "hi"})

    phase.chat()

    mocks["command"].assert_called_once_with("SAY", {"message": "hi"})
    mocks["respond"].assert_not_called()
    mocks["render"].assert_not_called()
