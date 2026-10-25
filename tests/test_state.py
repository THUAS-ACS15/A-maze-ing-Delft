"""Tests for ``src/state.py``."""

import json
from datetime import timedelta
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
        "player": {"current_room": "lobby", "inventory": [], "move": [], "forward": []},
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
    ("filename", "expected_name"),
    [
        pytest.param("custom", "custom.json", id="explicit"),
        pytest.param(None, "polaris_save_slot_1.json", id="default-generated"),
    ],
)
def test_save(monkeypatch, tmp_path, filename, expected_name):
    save_dir = tmp_path / "saves"
    game_state = _make_state()
    game_state["player"]["id"] = 7
    game_state["player"]["name"] = "polaris"
    monkeypatch.setattr(state_module, "state", game_state)
    monkeypatch.setattr(state_module, "SAVE_DIR", save_dir)
    monkeypatch.setattr(state_module, "colorize", lambda text, color_code=None: text)
    monkeypatch.setattr(room_module, "render", Mock())
    create_save = Mock()
    monkeypatch.setattr(state_module, "create_save", create_save)

    state_module.save({"target": filename})

    save_path = save_dir / expected_name
    assert json.loads(save_path.read_text(encoding="utf-8")) == game_state
    create_save.assert_called_once_with(save_path.stem, 7)


def test_save_requires_registration(monkeypatch, tmp_path):
    save_dir = tmp_path / "saves"
    monkeypatch.setattr(state_module, "state", _make_state())
    monkeypatch.setattr(state_module, "SAVE_DIR", save_dir)
    monkeypatch.setattr(state_module, "colorize", lambda text, color_code=None: text)
    render = Mock()
    monkeypatch.setattr(room_module, "render", render)
    create_save = Mock()
    monkeypatch.setattr(state_module, "create_save", create_save)

    state_module.save({"target": "custom"})

    assert "register" in render.call_args.args[0].lower()
    assert not (save_dir / "custom.json").exists()
    create_save.assert_not_called()


def test_save_reports_error_when_file_exists(monkeypatch, tmp_path):
    save_dir = tmp_path / "saves"
    save_dir.mkdir()
    (save_dir / "custom.json").write_text("{}", encoding="utf-8")
    game_state = _make_state()
    game_state["player"]["id"] = 7
    monkeypatch.setattr(state_module, "state", game_state)
    monkeypatch.setattr(state_module, "SAVE_DIR", save_dir)
    monkeypatch.setattr(state_module, "colorize", lambda text, color_code=None: text)
    render = Mock()
    monkeypatch.setattr(room_module, "render", render)
    create_save = Mock()
    monkeypatch.setattr(state_module, "create_save", create_save)

    state_module.save({"target": "custom"})

    create_save.assert_not_called()
    assert "unexpected error" in render.call_args.args[0].lower()


def test_save_without_details_generates_slot(monkeypatch, tmp_path):
    save_dir = tmp_path / "saves"
    game_state = _make_state()
    game_state["player"]["id"] = 7
    game_state["player"]["name"] = "polaris"
    monkeypatch.setattr(state_module, "state", game_state)
    monkeypatch.setattr(state_module, "SAVE_DIR", save_dir)
    monkeypatch.setattr(state_module, "colorize", lambda text, color_code=None: text)
    monkeypatch.setattr(room_module, "render", Mock())
    create_save = Mock()
    monkeypatch.setattr(state_module, "create_save", create_save)

    state_module.save()

    assert (save_dir / "polaris_save_slot_1.json").exists()
    create_save.assert_called_once_with("polaris_save_slot_1", 7)


def test_save_increments_slot_number(monkeypatch, tmp_path):
    save_dir = tmp_path / "saves"
    game_state = _make_state()
    game_state["player"]["id"] = 7
    game_state["player"]["name"] = "polaris"
    monkeypatch.setattr(state_module, "state", game_state)
    monkeypatch.setattr(state_module, "SAVE_DIR", save_dir)
    monkeypatch.setattr(state_module, "colorize", lambda text, color_code=None: text)
    monkeypatch.setattr(room_module, "render", Mock())
    create_save = Mock()
    monkeypatch.setattr(state_module, "create_save", create_save)

    state_module.save({"target": None})
    state_module.save({"target": None})

    assert sorted(p.name for p in save_dir.glob("polaris_save_slot_*.json")) == [
        "polaris_save_slot_1.json",
        "polaris_save_slot_2.json",
    ]
    assert [call.args[0] for call in create_save.call_args_list] == [
        "polaris_save_slot_1",
        "polaris_save_slot_2",
    ]


def test_save_skips_existing_generated_slot(monkeypatch, tmp_path):
    save_dir = tmp_path / "saves"
    save_dir.mkdir()
    (save_dir / "polaris_save_slot_1.json").write_text("{}", encoding="utf-8")
    (save_dir / "polaris_save_slot_backup.json").write_text("{}", encoding="utf-8")
    game_state = _make_state()
    game_state["player"]["id"] = 7
    game_state["player"]["name"] = "polaris"
    monkeypatch.setattr(state_module, "state", game_state)
    monkeypatch.setattr(state_module, "SAVE_DIR", save_dir)
    monkeypatch.setattr(state_module, "colorize", lambda text, color_code=None: text)
    monkeypatch.setattr(room_module, "render", Mock())
    create_save = Mock()
    monkeypatch.setattr(state_module, "create_save", create_save)

    state_module.save({"target": None})

    assert (save_dir / "polaris_save_slot_2.json").exists()
    create_save.assert_called_once_with("polaris_save_slot_2", 7)


def test_list_saves_requires_registration(monkeypatch):
    out = Mock()
    get_user_saves = Mock()
    monkeypatch.setattr(
        state_module, "state", {"player": {}, "terminal_width": 80}
    )
    monkeypatch.setattr(state_module, "colorize", lambda text, color_code=None: text)
    monkeypatch.setattr(state_module, "header", Mock())
    monkeypatch.setattr(state_module, "out", out)
    monkeypatch.setattr(state_module, "get_user_saves", get_user_saves)

    state_module.list_saves()

    get_user_saves.assert_not_called()
    assert "register" in out.call_args.args[0].lower()


def test_list_saves_prints_rows(monkeypatch, capsys):
    out = Mock()
    rows = [
        {"slot": "slot1", "created_at": "2026-10-24T10:30:43.756Z"},
        {"slot": "slot2", "created_at": "2026-10-25T11:00:00.000Z"},
    ]
    get_user_saves = Mock(return_value=rows)
    monkeypatch.setattr(
        state_module, "state", {"player": {"id": 7}, "terminal_width": 80}
    )
    monkeypatch.setattr(state_module, "colorize", lambda text, color_code=None: text)
    monkeypatch.setattr(state_module, "header", Mock())
    monkeypatch.setattr(state_module, "out", out)
    monkeypatch.setattr(state_module, "get_user_saves", get_user_saves)
    monkeypatch.setattr(state_module, "format_timestamp", lambda iso: iso[:10])

    state_module.list_saves()

    get_user_saves.assert_called_once_with(7)
    printed = capsys.readouterr().out
    assert "slot1" in printed
    assert "slot2" in printed
    assert "2026-10-24" in printed
    out.assert_called_once_with()


def test_list_saves_reports_empty(monkeypatch):
    out = Mock()
    get_user_saves = Mock(return_value=[])
    monkeypatch.setattr(
        state_module, "state", {"player": {"id": 7}, "terminal_width": 80}
    )
    monkeypatch.setattr(state_module, "colorize", lambda text, color_code=None: text)
    monkeypatch.setattr(state_module, "header", Mock())
    monkeypatch.setattr(state_module, "out", out)
    monkeypatch.setattr(state_module, "get_user_saves", get_user_saves)

    state_module.list_saves()

    get_user_saves.assert_called_once_with(7)
    assert "no saved slot" in out.call_args.args[0].lower()


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


def _load_state(user_id=7):
    return {
        "player": {"id": user_id, "name": "polaris", "current_room": "front_desk"},
        "rooms": {},
        "game_state": {},
    }


def test_load_requires_registration(monkeypatch):
    render = Mock()
    get_user_save = Mock()
    monkeypatch.setattr(state_module, "state", {"player": {}})
    monkeypatch.setattr(state_module, "colorize", lambda text=None, color_code=None: text)
    monkeypatch.setattr(room_module, "render", render)
    monkeypatch.setattr(state_module, "get_user_save", get_user_save)

    state_module.load({"target": "slot1"})

    get_user_save.assert_not_called()
    assert "register" in render.call_args.args[0].lower()


def test_load_rejects_slot_not_owned(monkeypatch):
    render = Mock()
    get_user_save = Mock(return_value=None)
    monkeypatch.setattr(state_module, "state", _load_state())
    monkeypatch.setattr(state_module, "colorize", lambda text=None, color_code=None: text)
    monkeypatch.setattr(room_module, "render", render)
    monkeypatch.setattr(state_module, "get_user_save", get_user_save)

    state_module.load({"target": "slot1"})

    get_user_save.assert_called_once_with(7, "slot1")
    assert "do not have any progress" in render.call_args.args[0].lower()


def test_load_reports_missing_file(monkeypatch, tmp_path):
    render = Mock()
    monkeypatch.setattr(state_module, "state", _load_state())
    monkeypatch.setattr(state_module, "SAVE_DIR", tmp_path)
    monkeypatch.setattr(state_module, "colorize", lambda text=None, color_code=None: text)
    monkeypatch.setattr(room_module, "render", render)
    monkeypatch.setattr(state_module, "get_user_save", Mock(return_value={"slot": "slot1"}))

    state_module.load({"target": "slot1"})

    assert "no saved progress" in render.call_args.args[0].lower()


def test_load_existing_file_updates_state_in_place(monkeypatch, tmp_path):
    save_dir = tmp_path / "saves"
    save_dir.mkdir()
    save_data = _make_state()
    (save_dir / "slot1.json").write_text(json.dumps(save_data), encoding="utf-8")
    game_state = _load_state()
    render = Mock()
    monkeypatch.setattr(state_module, "state", game_state)
    monkeypatch.setattr(state_module, "SAVE_DIR", save_dir)
    monkeypatch.setattr(state_module, "colorize", lambda text=None, color_code=None: text)
    monkeypatch.setattr(room_module, "render", render)
    monkeypatch.setattr(state_module, "get_user_save", Mock(return_value={"slot": "slot1"}))

    state_module.load({"target": "slot1"})

    assert state_module.state is game_state
    assert game_state == save_data
    assert "loaded" in render.call_args.args[0].lower()


def test_load_strips_json_suffix(monkeypatch, tmp_path):
    save_dir = tmp_path / "saves"
    save_dir.mkdir()
    save_data = _make_state()
    (save_dir / "slot1.json").write_text(json.dumps(save_data), encoding="utf-8")
    get_user_save = Mock(return_value={"slot": "slot1"})
    monkeypatch.setattr(state_module, "state", _load_state())
    monkeypatch.setattr(state_module, "SAVE_DIR", save_dir)
    monkeypatch.setattr(state_module, "colorize", lambda text=None, color_code=None: text)
    monkeypatch.setattr(room_module, "render", Mock())
    monkeypatch.setattr(state_module, "get_user_save", get_user_save)

    state_module.load({"target": "slot1.json"})

    get_user_save.assert_called_once_with(7, "slot1")


def test_move_direction(monkeypatch, move_env):
    game_state = _move_state()
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "north"})

    assert game_state["player"]["current_room"] == "classroom"
    assert game_state["player"]["move"] == ["lobby"]
    move_env.assert_called_once_with()


def test_move_by_room_id(monkeypatch, move_env):
    game_state = _move_state()
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "classroom"})

    assert game_state["player"]["current_room"] == "classroom"
    assert game_state["player"]["move"] == ["lobby"]
    move_env.assert_called_once_with()


def test_move_invalid_destination(monkeypatch, move_env):
    game_state = _move_state()
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "nowhere"})

    assert game_state["player"]["current_room"] == "lobby"
    assert (
        move_env.call_args.kwargs["text"]
        == "You cannot go to nowhere from here. "
        "Adjacent: classroom, lab, restricted_room."
    )


def test_move_invalid_direction(monkeypatch, move_env):
    game_state = _move_state()
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "west"})

    assert game_state["player"]["current_room"] == "lobby"
    assert (
        move_env.call_args.kwargs["text"]
        == "You cannot go to west from here. "
        "Adjacent: classroom, lab, restricted_room."
    )


def test_move_unknown_target(monkeypatch, move_env):
    game_state = {
        "player": {"current_room": "lobby", "inventory": [], "move": [], "forward": []},
        "rooms": {"lobby": {"exits": {"north": "void"}}},
    }
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "north"})

    assert game_state["player"]["current_room"] == "lobby"
    assert move_env.call_args.kwargs["text"] == "Unknown destination 'void'."


def test_move_requires_locked(monkeypatch, move_env):
    game_state = _move_state()
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "lab"})

    assert game_state["player"]["current_room"] == "lobby"
    assert (
        move_env.call_args.kwargs["text"]
        == "The door is locked. Access requires: keycard_lvl1."
    )


def test_move_requires_unlocked(monkeypatch, move_env):
    game_state = _move_state()
    game_state["player"]["inventory"] = ["keycard_lvl1"]
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "lab"})

    assert game_state["player"]["current_room"] == "lab"
    assert game_state["player"]["move"] == ["lobby"]
    move_env.assert_called_once_with()


def test_move_restricted_locked(monkeypatch, move_env):
    game_state = _move_state()
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "south"})

    assert game_state["player"]["current_room"] == "lobby"
    assert move_env.call_args.kwargs["text"] == "The door is locked."


def test_move_back_retraces_history(monkeypatch, move_env):
    game_state = _move_state()
    game_state["player"].update(
        current_room="lab", move=["lobby", "classroom"], forward=[]
    )
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "back"})

    assert game_state["player"]["current_room"] == "classroom"
    assert game_state["player"]["move"] == ["lobby"]
    assert game_state["player"]["forward"] == ["lab"]

    state_module.move({"target": "back"})

    assert game_state["player"]["current_room"] == "lobby"
    assert game_state["player"]["move"] == []
    assert game_state["player"]["forward"] == ["lab", "classroom"]
    assert move_env.call_count == 2


def test_move_forward_replays_history(monkeypatch, move_env):
    game_state = _move_state()
    game_state["player"].update(
        current_room="lobby", move=[], forward=["lab", "classroom"]
    )
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "forward"})

    assert game_state["player"]["current_room"] == "classroom"
    assert game_state["player"]["move"] == ["lobby"]
    assert game_state["player"]["forward"] == ["lab"]

    state_module.move({"target": "forward"})

    assert game_state["player"]["current_room"] == "lab"
    assert game_state["player"]["move"] == ["lobby", "classroom"]
    assert game_state["player"]["forward"] == []
    assert move_env.call_count == 2


def test_move_back_with_empty_history(monkeypatch, move_env):
    game_state = _move_state()
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "back"})

    assert game_state["player"]["current_room"] == "lobby"
    assert (
        move_env.call_args.kwargs["text"]
        == "You have no previous room to go back to."
    )


def test_move_forward_with_empty_history(monkeypatch, move_env):
    game_state = _move_state()
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "forward"})

    assert game_state["player"]["current_room"] == "lobby"
    assert (
        move_env.call_args.kwargs["text"]
        == "You have no forward room to go to."
    )


def test_move_new_move_clears_forward_history(monkeypatch, move_env):
    game_state = _move_state()
    game_state["player"].update(
        current_room="classroom", move=["lobby"], forward=["lab"]
    )
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "south"})

    assert game_state["player"]["current_room"] == "lobby"
    assert game_state["player"]["move"] == ["lobby", "classroom"]
    assert game_state["player"]["forward"] == []
    move_env.assert_called_once_with()


def test_move_back_without_forward_field(monkeypatch, move_env):
    game_state = _move_state()
    game_state["player"].update(current_room="classroom", move=["lobby"])
    del game_state["player"]["forward"]
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "back"})

    assert game_state["player"]["current_room"] == "lobby"
    assert game_state["player"]["move"] == []
    assert game_state["player"]["forward"] == ["classroom"]


def test_move_back_unknown_history_room(monkeypatch, move_env):
    game_state = _move_state()
    game_state["player"].update(
        current_room="classroom", move=["ghost"], forward=[]
    )
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "back"})

    assert game_state["player"]["current_room"] == "classroom"
    assert game_state["player"]["move"] == ["ghost"]
    assert game_state["player"]["forward"] == []
    assert move_env.call_args.kwargs["text"] == "Unknown destination 'ghost'."


def test_move_forward_unknown_history_room(monkeypatch, move_env):
    game_state = _move_state()
    game_state["player"].update(
        current_room="lobby", move=[], forward=["ghost"]
    )
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "forward"})

    assert game_state["player"]["current_room"] == "lobby"
    assert game_state["player"]["move"] == []
    assert game_state["player"]["forward"] == ["ghost"]
    assert move_env.call_args.kwargs["text"] == "Unknown destination 'ghost'."


def test_move_back_bypasses_locked_door(monkeypatch, move_env):
    game_state = _move_state()
    game_state["player"].update(
        current_room="lobby", move=["lab"], forward=[]
    )
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "back"})

    assert game_state["player"]["current_room"] == "lab"
    assert game_state["player"]["forward"] == ["lobby"]
    move_env.assert_called_once_with()


def test_move_forward_bypasses_locked_door(monkeypatch, move_env):
    game_state = _move_state()
    game_state["player"].update(
        current_room="lobby", move=[], forward=["restricted_room"]
    )
    monkeypatch.setattr(state_module, "state", game_state)

    state_module.move({"target": "forward"})

    assert game_state["player"]["current_room"] == "restricted_room"
    assert game_state["player"]["move"] == ["lobby"]
    move_env.assert_called_once_with()
