"""Tests for ``src/state.py``."""

import json
import os
from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock

import pytest

import src.parser as parser_module
import src.room as room_module
import src.state as state_module

DIRECTIONS = {"north": "north", "south": "south", "east": "east", "west": "west"}


def _make_state(
    rooms=None,
    current_room="lobby",
    inventory=None,
    timestamp="2024-01-01T00:00:00+00:00",
    is_ready=False,
    phase="EXPLORATION",
):
    return {
        "player": {
            "current_room": current_room,
            "inventory": list(inventory or []),
            "move": [],
        },
        "rooms": rooms if rooms is not None else {"lobby": {}, "classroom": {}},
        "game_state": {
            "timestamp": timestamp,
            "duration": "00:00:00",
            "phase": phase,
            "phases": {"assembly": {"activated": False}},
        },
        "workbench": {"is_ready": is_ready},
    }


def _move_state():
    return {
        "player": {"current_room": "lobby", "inventory": [], "move": []},
        "rooms": {
            "lobby": {
                "exits": {
                    "north": "classroom",
                    "east": "lab",
                    "south": "restricted_room",
                }
            },
            "classroom": {"exits": {"south": "lobby"}},
            "lab": {"exits": {"west": "lobby"}, "requires": "keycard_lvl1"},
            "restricted_room": {"exits": {"north": "lobby"}, "restricted": True},
        },
    }


@pytest.fixture
def move_env(monkeypatch):
    """Patch move()'s locally-imported dependencies."""
    render_mock = Mock()
    monkeypatch.setattr(
        state_module, "colorize", lambda text=None, color_code=None: text
    )
    monkeypatch.setattr(room_module, "render", render_mock)
    monkeypatch.setattr(parser_module, "resolve_room_target", lambda raw: raw)
    monkeypatch.setattr(parser_module, "ROOM_ALIASES", DIRECTIONS)
    return render_mock


@pytest.mark.parametrize("precreate", [False, True], ids=["missing", "zero-byte"])
def test_initialize_creates_user_state_from_default(monkeypatch, tmp_path, precreate):
    user_path = tmp_path / "user_state.json"
    default_path = tmp_path / "default.json"
    help_path = tmp_path / "help.json"
    default_data = {"rooms": {"lobby": {"name": "Lobby"}}, "game_state": {}}
    default_path.write_text(json.dumps(default_data))
    help_path.write_text(json.dumps([]))
    if precreate:
        user_path.write_text("")

    monkeypatch.setattr(state_module, "USER_STATE_PATH", user_path)
    monkeypatch.setattr(state_module, "DEFAULT_GAME_STATE_PATH", default_path)
    monkeypatch.setattr(state_module, "HELP_COMMANDS_PATH", help_path)
    monkeypatch.setattr(state_module, "state", {})
    monkeypatch.setattr(state_module, "help_commands", [])

    state_module.initialize()

    assert json.loads(user_path.read_text()) == default_data
    assert state_module.state == default_data
    assert state_module.help_commands == []


def test_initialize_keeps_existing_state(monkeypatch, tmp_path):
    user_path = tmp_path / "user_state.json"
    user_path.write_text(json.dumps({"rooms": {}}))
    help_path = tmp_path / "help.json"
    help_path.write_text(json.dumps([{"title": "Movement"}]))

    existing_state = {"custom": True}
    existing_help = [{"title": "Already loaded"}]

    monkeypatch.setattr(state_module, "USER_STATE_PATH", user_path)
    monkeypatch.setattr(
        state_module, "DEFAULT_GAME_STATE_PATH", tmp_path / "default.json"
    )
    monkeypatch.setattr(state_module, "HELP_COMMANDS_PATH", help_path)
    monkeypatch.setattr(state_module, "state", existing_state)
    monkeypatch.setattr(state_module, "help_commands", existing_help)

    state_module.initialize()

    assert state_module.state is existing_state
    assert state_module.help_commands == existing_help


def test_initialize_loads_help_commands(monkeypatch, tmp_path):
    user_path = tmp_path / "user_state.json"
    user_path.write_text(json.dumps({"rooms": {}}))
    help_path = tmp_path / "help.json"
    help_data = [{"title": "Movement", "commands": []}]
    help_path.write_text(json.dumps(help_data))

    monkeypatch.setattr(state_module, "USER_STATE_PATH", user_path)
    monkeypatch.setattr(
        state_module, "DEFAULT_GAME_STATE_PATH", tmp_path / "default.json"
    )
    monkeypatch.setattr(state_module, "HELP_COMMANDS_PATH", help_path)
    monkeypatch.setattr(state_module, "state", {"rooms": {}})
    monkeypatch.setattr(state_module, "help_commands", [])

    state_module.initialize()

    assert state_module.help_commands == help_data


@pytest.mark.parametrize(
    ("duration_value", "expected_duration"),
    [
        pytest.param(timedelta(minutes=5), "0:05:00", id="timedelta"),
        pytest.param("", "00:00:00", id="empty-fallback"),
    ],
)
def test_auto_updates_duration(
    monkeypatch, tmp_path, duration_value, expected_duration
):
    user_path = tmp_path / "user_state.json"
    game_state = _make_state(timestamp="2024-01-01T00:00:00+00:00")
    monkeypatch.setattr(state_module, "state", game_state)
    monkeypatch.setattr(state_module, "USER_STATE_PATH", user_path)
    monkeypatch.setattr(
        state_module, "calculate_duration", Mock(return_value=duration_value)
    )

    state_module.auto()

    assert game_state["game_state"]["duration"] == expected_duration
    assert json.loads(user_path.read_text()) == game_state


def test_auto_advances_phase_when_ready(monkeypatch, tmp_path):
    game_state = _make_state(is_ready=True, phase="EXPLORATION")
    monkeypatch.setattr(state_module, "state", game_state)
    monkeypatch.setattr(state_module, "USER_STATE_PATH", tmp_path / "user_state.json")
    monkeypatch.setattr(
        state_module, "calculate_duration", Mock(return_value=timedelta(0))
    )

    state_module.auto()

    assert game_state["game_state"]["phase"] == "ASSEMBLY"
    assert game_state["game_state"]["phases"]["assembly"]["activated"] is True


@pytest.mark.parametrize(
    ("is_ready", "phase"),
    [
        pytest.param(False, "EXPLORATION", id="not-ready"),
        pytest.param(True, "ASSEMBLY", id="already-assembly"),
    ],
)
def test_auto_does_not_advance_phase(monkeypatch, tmp_path, is_ready, phase):
    game_state = _make_state(is_ready=is_ready, phase=phase)
    monkeypatch.setattr(state_module, "state", game_state)
    monkeypatch.setattr(state_module, "USER_STATE_PATH", tmp_path / "user_state.json")
    monkeypatch.setattr(
        state_module, "calculate_duration", Mock(return_value=timedelta(0))
    )

    state_module.auto()

    assert game_state["game_state"]["phase"] == phase
    assert game_state["game_state"]["phases"]["assembly"]["activated"] is False


@pytest.mark.parametrize(
    ("call_kwargs", "filename"),
    [
        pytest.param({}, "save_slot_1.json", id="default"),
        pytest.param({"filename": "custom.json"}, "custom.json", id="explicit"),
    ],
)
def test_save(monkeypatch, tmp_path, call_kwargs, filename):
    save_dir = tmp_path / "saves"
    game_state = _make_state()
    monkeypatch.setattr(state_module, "state", game_state)
    monkeypatch.setattr(state_module, "SAVE_DIR", save_dir)

    ok, message = state_module.save(**call_kwargs)

    save_path = os.path.join(save_dir, filename)
    assert ok is True
    assert message == f"[System] Game saved to {save_path}"
    assert json.loads(Path(save_path).read_text(encoding="utf-8")) == game_state


def test_spawn_sets_timestamp_when_missing(monkeypatch):
    game_state = _make_state(timestamp=None)
    monkeypatch.setattr(state_module, "state", game_state)

    result = state_module.spawn()

    assert result == "lobby"
    assert game_state["game_state"]["timestamp"]
    assert game_state["game_state"]["timestamp"] != ""


def test_spawn_preserves_timestamp(monkeypatch):
    timestamp = "2024-01-01T00:00:00+00:00"
    game_state = _make_state(timestamp=timestamp)
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.spawn()

    assert game_state["game_state"]["timestamp"] == timestamp


@pytest.mark.parametrize(
    ("current_room", "expected"),
    [
        pytest.param("lobby", "lobby", id="valid-lobby"),
        pytest.param("classroom", "classroom", id="valid-classroom"),
    ],
)
def test_spawn_returns_valid_room(monkeypatch, current_room, expected):
    game_state = _make_state(current_room=current_room)
    monkeypatch.setattr(state_module, "state", game_state)

    assert state_module.spawn() == expected


@pytest.mark.parametrize(
    "current_room",
    [
        pytest.param(None, id="none"),
        pytest.param(42, id="non-string"),
        pytest.param("unknown", id="not-in-rooms"),
    ],
)
def test_spawn_falls_back_to_first_room(monkeypatch, current_room):
    game_state = _make_state(current_room=current_room)
    monkeypatch.setattr(state_module, "state", game_state)

    assert state_module.spawn() == "lobby"


def test_spawn_empty_rooms_defaults_lobby(monkeypatch):
    game_state = _make_state(rooms={}, current_room=None)
    monkeypatch.setattr(state_module, "state", game_state)

    assert state_module.spawn() == "lobby"


def test_load_missing_file(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(state_module, "SAVE_DIR", tmp_path)

    assert state_module.load("nope.json") is False
    assert "No save file found." in capsys.readouterr().out


def test_load_existing_file(monkeypatch, tmp_path, capsys):
    save_dir = tmp_path / "saves"
    save_dir.mkdir()
    save_data = _make_state()
    (save_dir / "slot.json").write_text(json.dumps(save_data), encoding="utf-8")
    monkeypatch.setattr(state_module, "SAVE_DIR", save_dir)
    monkeypatch.setattr(state_module, "state", {})

    assert state_module.load("slot.json") is True
    assert state_module.state == save_data
    assert "Loaded saved file" in capsys.readouterr().out


def test_move_direction(monkeypatch, move_env):
    game_state = _move_state()
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move("north")

    assert game_state["player"]["current_room"] == "classroom"
    assert game_state["player"]["move"] == ["lobby"]
    move_env.assert_called_once_with()


def test_move_by_room_id(monkeypatch, move_env):
    game_state = _move_state()
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move("classroom")

    assert game_state["player"]["current_room"] == "classroom"
    assert game_state["player"]["move"] == ["lobby"]
    move_env.assert_called_once_with()


def test_move_invalid_destination(monkeypatch, move_env):
    game_state = _move_state()
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move("nowhere")

    assert game_state["player"]["current_room"] == "lobby"
    assert (
        move_env.call_args.kwargs["text"]
        == "You cannot go to nowhere from here. "
        "Adjacent: classroom, lab, restricted_room."
    )


def test_move_invalid_direction(monkeypatch, move_env):
    game_state = _move_state()
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move("west")

    assert game_state["player"]["current_room"] == "lobby"
    assert (
        move_env.call_args.kwargs["text"]
        == "You cannot go to west from here. "
        "Adjacent: classroom, lab, restricted_room."
    )


def test_move_unknown_target(monkeypatch, move_env):
    game_state = {
        "player": {"current_room": "lobby", "inventory": [], "move": []},
        "rooms": {"lobby": {"exits": {"north": "void"}}},
    }
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move("north")

    assert game_state["player"]["current_room"] == "lobby"
    assert move_env.call_args.kwargs["text"] == "Unknown destination 'void'."


def test_move_requires_locked(monkeypatch, move_env):
    game_state = _move_state()
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move("lab")

    assert game_state["player"]["current_room"] == "lobby"
    assert (
        move_env.call_args.kwargs["text"]
        == "The door is locked. Access requires: keycard_lvl1."
    )


def test_move_requires_unlocked(monkeypatch, move_env):
    game_state = _move_state()
    game_state["player"]["inventory"] = ["keycard_lvl1"]
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move("lab")

    assert game_state["player"]["current_room"] == "lab"
    assert game_state["player"]["move"] == ["lobby"]
    move_env.assert_called_once_with()


def test_move_restricted_locked(monkeypatch, move_env):
    game_state = _move_state()
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move("south")

    assert game_state["player"]["current_room"] == "lobby"
    assert move_env.call_args.kwargs["text"] == "The door is locked."
