"""Tests for ``src/engine.py``."""

import builtins
import json
from unittest.mock import Mock

import pytest

import src.engine as engine
import src.phase as phase_module

HELP_GROUPS = [
    {
        "title": "Movement",
        "commands": [
            {"command": "go", "description": "Move", "example": "go north"}
        ],
    },
    {
        "title": "Assembly",
        "commands": [
            {"command": "use", "description": "Install", "example": "use x"}
        ],
    },
]


def _out_texts(out_mock):
    return [call.args[0] for call in out_mock.call_args_list if call.args]


def _status_rows(out_mock):
    rows = {}
    for text in _out_texts(out_mock):
        label, separator, value = text.strip().partition(":")
        if separator and not label.startswith("•"):
            rows[label] = value.strip()
    return rows


def _duration(value="00:00:00"):
    return {"last_write": None, "value": value, "pause": False}


def _block_rich_import(monkeypatch):
    """Simulate rich not being installed for helper()'s fallback path."""
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "rich.console":
            raise ModuleNotFoundError("No module named 'rich.console'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)


@pytest.fixture
def rendered(monkeypatch):
    """Patch engine's rendering helpers."""
    out_mock = Mock()
    header_mock = Mock()
    monkeypatch.setattr(engine, "out", out_mock)
    monkeypatch.setattr(engine, "header", header_mock)
    monkeypatch.setattr(engine, "colorize", lambda text=None, color_code=None: text)
    return {"out": out_mock, "header": header_mock}


@pytest.fixture
def scoreboard_env(monkeypatch):
    mocks = {
        "header": Mock(),
        "out": Mock(),
        "get_scoreboard_entries": Mock(return_value=[]),
        "get_user": Mock(return_value=None),
        "state": {"terminal_width": 80},
    }
    for name, mock in mocks.items():
        monkeypatch.setattr(engine, name, mock)
    monkeypatch.setattr(engine, "colorize", lambda text=None, color_code=None: text)
    return mocks


@pytest.fixture
def inspect_env(monkeypatch):
    render_mock = Mock()
    workbench_mock = Mock()
    monkeypatch.setattr(engine, "render", render_mock)
    monkeypatch.setattr(engine, "workbench", workbench_mock)
    monkeypatch.setattr(engine, "colorize", lambda text=None, color_code=None: text)
    monkeypatch.setattr("src.assets.logo.logo", "LOGO")
    return {"render": render_mock, "workbench": workbench_mock}


@pytest.fixture
def use_env(monkeypatch):
    desk_mock = Mock()
    workbench_mock = Mock()
    render_mock = Mock()
    monkeypatch.setattr(engine, "use_desk_code", desk_mock)
    monkeypatch.setattr(engine, "use_on_workbench", workbench_mock)
    monkeypatch.setattr(engine, "render", render_mock)
    monkeypatch.setattr(engine, "colorize", lambda text=None, color_code=None: text)
    return {"desk": desk_mock, "workbench": workbench_mock, "render": render_mock}


@pytest.fixture
def item_env(monkeypatch):
    render_mock = Mock()
    monkeypatch.setattr(engine, "render", render_mock)
    monkeypatch.setattr(engine, "colorize", lambda text=None, color_code=None: text)
    return render_mock


@pytest.fixture
def command_env(monkeypatch):
    mocks = {
        "render": Mock(),
        "helper": Mock(),
        "scoreboard": Mock(),
        "status": Mock(),
        "inventory": Mock(),
        "use": Mock(),
        "register": Mock(),
        "login": Mock(),
        "logout": Mock(),
        "save": Mock(),
        "list_saves": Mock(),
        "load": Mock(),
        "inspect": Mock(),
        "take": Mock(),
        "drop": Mock(),
        "move": Mock(),
        "restart": Mock(),
    }
    for name, mock in mocks.items():
        monkeypatch.setattr(engine, name, mock)
    return mocks


def _status_full_state():
    return {
        "terminal_width": 120,
        "player": {
            "id": 5,
            "name": "sadanand",
            "current_room": "teachers_room_1",
            "inventory": ["chassis_frame", "keycard_lvl1", "mystery"],
            "move": ["lobby", "teachers_room_1", "lobby"],
        },
        "rooms": {
            "lobby": {"name": "Lobby"},
            "teachers_room_1": {"name": "Teachers Room 1"},
        },
        "items": {
            "chassis_frame": {
                "name": "Robot Chassis Frame",
                "is_assembly_part": True,
            },
            "keycard_lvl1": {
                "name": "Level-1 Staff Keycard",
                "is_assembly_part": False,
            },
        },
        "flags": {
            "tr1_desk_unlocked": True,
            "tr2_whiteboard_inspected": False,
            "lab_power_on": True,
        },
        "workbench": {
            "installed_parts": ["chassis_frame"],
            "required_parts": ["chassis_frame", "battery_pack"],
            "is_ready": False,
        },
        "game_state": {
            "timestamp": "2026-10-26T13:34:05.696941+00:00",
            "duration": _duration("7:51:37"),
            "phase": "EXPLORATION",
        },
    }


def _visited_state(count: int, width: int = 120) -> dict:
    rooms = {
        f"room_{index}": {"name": f"Room {index}"}
        for index in range(1, count + 1)
    }
    return {
        "terminal_width": width,
        "player": {
            "id": None,
            "name": "guest",
            "current_room": f"room_{count}",
            "inventory": [],
            "move": [f"room_{index}" for index in range(1, count + 1)],
        },
        "rooms": rooms,
        "items": {},
        "flags": {},
        "workbench": {
            "installed_parts": [],
            "required_parts": [],
            "is_ready": False,
        },
        "game_state": {
            "timestamp": None,
            "duration": _duration(),
            "phase": "EXPLORATION",
        },
    }


def _inspect_state(current_room, unlocked=False):
    return {
        "player": {"current_room": current_room},
        "rooms": {
            "lobby": {"interactables": {"terminal": "TERMINAL TEXT"}},
            "teachers_room_1": {"interactables": {"desk": {"hint": "DESK HINT"}}},
            "teachers_room_2": {"interactables": {"whiteboard": "WHITEBOARD TEXT"}},
            "front_desk": {"interactables": {"receptionist": "RECEPTIONIST TEXT"}},
            "lab_d2_001": {},
        },
        "flags": {
            "tr1_desk_unlocked": unlocked,
            "tr2_whiteboard_inspected": False,
        },
    }


@pytest.mark.parametrize(
    ("message", "expected_prompt"),
    [
        pytest.param(None, "\n> ", id="no-message"),
        pytest.param("Enter", "\nEnter >", id="with-message"),
    ],
)
def test_prompt(monkeypatch, message, expected_prompt):
    captured = {}

    def fake_input(prompt_text):
        captured["prompt"] = prompt_text
        return "  hello  "

    monkeypatch.setattr(builtins, "input", fake_input)

    result = engine.prompt(message)

    assert result == "hello"
    assert captured["prompt"] == expected_prompt


def test_inventory_empty(monkeypatch, rendered):
    monkeypatch.setattr(
        engine,
        "state",
        {
            "terminal_width": 80,
            "game_state": {
                "phase": "EXPLORATION",
                "duration": _duration(),
            },
            "player": {"inventory": []},
        },
    )

    engine.inventory()

    rendered["header"].assert_called_once_with("INVENTORY")
    assert any(
        "Your inventory is currently empty." in text
        for text in _out_texts(rendered["out"])
    )


def test_inventory_populated(monkeypatch, rendered):
    monkeypatch.setattr(
        engine,
        "state",
        {
            "terminal_width": 80,
            "game_state": {
                "phase": "EXPLORATION",
                "duration": _duration("00:05:00"),
            },
            "player": {"inventory": ["chassis_frame", "keycard_lvl1"]},
            "items": {
                "chassis_frame": {
                    "name": "Robot Chassis Frame",
                    "description": "An aluminum skeleton.",
                    "is_assembly_part": True,
                },
                "keycard_lvl1": {
                    "name": "Level-1 Staff Keycard",
                    "description": "A magnetic keycard.",
                    "is_assembly_part": False,
                },
            },
            "workbench": {"required_parts": ["chassis_frame", "battery_pack"]},
        },
    )

    engine.inventory()

    texts = _out_texts(rendered["out"])
    assert " • Robot Chassis Frame [ASSEMBLY PART]" in texts
    assert "   An aluminum skeleton." in texts
    assert " • Level-1 Staff Keycard" in texts
    assert "   A magnetic keycard." in texts
    assert any("Assembly Components in Inventory: 1/2" in text for text in texts)


@pytest.mark.parametrize(
    ("phase", "assembly_visible"),
    [
        pytest.param("EXPLORATION", False, id="exploration-hides-assembly"),
        pytest.param("ASSEMBLY", True, id="assembly-shows-assembly"),
    ],
)
def test_helper_filter_and_fallback(monkeypatch, rendered, phase, assembly_visible):
    _block_rich_import(monkeypatch)
    monkeypatch.setattr(engine, "help_commands", HELP_GROUPS)
    monkeypatch.setattr(
        engine,
        "state",
        {"game_state": {"phase": phase, "duration": _duration()}},
    )

    engine.helper()

    texts = _out_texts(rendered["out"])
    assert texts[0] == "Available Commands:"
    assert any("[Movement]" in text for text in texts)
    assert bool([text for text in texts if "[Assembly]" in text]) is assembly_visible


def test_helper_rich_path(monkeypatch, rendered):
    console_cls = Mock()
    table_cls = Mock()
    monkeypatch.setattr("rich.console.Console", console_cls)
    monkeypatch.setattr("rich.table.Table", table_cls)
    monkeypatch.setattr(engine, "help_commands", HELP_GROUPS)
    monkeypatch.setattr(
        engine,
        "state",
        {"game_state": {"phase": "EXPLORATION", "duration": _duration()}},
    )

    engine.helper()

    rendered["header"].assert_called_once_with("HELP MENU")
    console_cls.return_value.print.assert_called_once_with(table_cls.return_value)
    table_cls.return_value.add_row.assert_called_once_with("go", "Move", "go north")


def test_scoreboard_empty(scoreboard_env):
    engine.scoreboard()

    scoreboard_env["header"].assert_called_once_with("GAME SCOREBOARD")
    assert _out_texts(scoreboard_env["out"]) == ["No entries found!".center(80)]
    scoreboard_env["get_user"].assert_not_called()


def test_scoreboard_table(scoreboard_env):
    scoreboard_env["get_scoreboard_entries"].return_value = [
        {
            "id": 1,
            "user_id": 10,
            "score": 100,
            "avg_room_time": "0:30",
            "exploration_time": "1:00",
            "assembly_time": "0:45",
        },
        {
            "id": 2,
            "user_id": 20,
            "score": 75,
            "avg_room_time": "0:40",
            "exploration_time": "2:00",
            "assembly_time": "1:00",
        },
    ]
    scoreboard_env["get_user"].side_effect = lambda user_id: {
        10: {"name": "Alice"},
        20: {"name": "Bob"},
    }[user_id]

    engine.scoreboard()

    scoreboard_env["header"].assert_called_once_with("GAME SCOREBOARD")
    texts = _out_texts(scoreboard_env["out"])
    assert texts[0].startswith("Rank")
    assert "Player" in texts[0]
    assert "Score" in texts[0]
    assert "Avg Room" in texts[0]
    assert "Exploration" in texts[0]
    assert "Assembly" in texts[0]
    assert texts[1].startswith("1")
    assert "Alice" in texts[1]
    assert "100" in texts[1]
    assert "0:30" in texts[1]
    assert "1:00" in texts[1]
    assert "0:45" in texts[1]
    assert texts[2].startswith("2")
    assert "Bob" in texts[2]
    assert "75" in texts[2]
    assert "0:40" in texts[2]
    assert "2:00" in texts[2]
    assert "1:00" in texts[2]
    assert [
        call.args[0] for call in scoreboard_env["get_user"].call_args_list
    ] == [10, 20]


def test_scoreboard_unknown_user(scoreboard_env):
    scoreboard_env["get_scoreboard_entries"].return_value = [
        {
            "id": 1,
            "user_id": 99,
            "score": 42,
            "avg_room_time": "0:30",
            "exploration_time": "1:00",
            "assembly_time": "0:45",
        },
    ]

    engine.scoreboard()

    texts = _out_texts(scoreboard_env["out"])
    assert texts[0].startswith("Rank")
    assert "Unknown (99)" in texts[1]
    assert "42" in texts[1]


def test_status_full(monkeypatch, rendered):
    monkeypatch.setattr(engine, "state", _status_full_state())

    engine.status()

    rendered["header"].assert_called_once_with("STATUS MENU")
    rows = _status_rows(rendered["out"])
    assert rows["Name"] == "Sadanand"
    assert rows["Room"] == "Teachers Room 1"
    assert rows["Phase"] == "EXPLORATION"
    assert rows["Started"] == "2026-10-26 13:34"
    assert rows["Time spent"] == "7:51:37"
    assert rows["Explored"] == "2/2 (100%)"
    assert rows["Visited"] == "Lobby, Teachers Room 1"
    assert rows["Challenges"] == (
        "2/3 Teachers Room 1 desk unlocked, Lab power restored"
    )
    assert rows["Assembly"] == "1/2 installed (not ready)"
    assert rows["Inventory"] == (
        "Robot Chassis Frame, Level-1 Staff Keycard, mystery"
    )
    assert rows["Assembly parts"] == "1"


def test_status_empty_state(monkeypatch, rendered):
    monkeypatch.setattr(
        engine,
        "state",
        {
            "terminal_width": 120,
            "player": {
                "id": None,
                "name": "guest",
                "current_room": "lobby",
                "inventory": [],
                "move": [],
            },
            "rooms": {"lobby": {"name": "Lobby"}},
            "items": {},
            "flags": {},
            "workbench": {
                "installed_parts": [],
                "required_parts": [],
                "is_ready": False,
            },
            "game_state": {
                "timestamp": None,
                "duration": _duration(),
                "phase": "EXPLORATION",
            },
        },
    )

    engine.status()

    rows = _status_rows(rendered["out"])
    assert rows["Name"] == "Guest"
    assert rows["Started"] == "Unknown"
    assert rows["Time spent"] == "00:00:00"
    assert rows["Explored"] == "1/1 (100%)"
    assert rows["Visited"] == "Lobby"
    assert rows["Challenges"] == "0/0"
    assert rows["Assembly"] == "0/0 installed (not ready)"
    assert rows["Inventory"] == "Empty"
    assert rows["Assembly parts"] == "0"


def test_status_ready_workbench(monkeypatch, rendered):
    monkeypatch.setattr(
        engine,
        "state",
        {
            "terminal_width": 120,
            "player": {
                "id": 1,
                "name": "alice",
                "current_room": "lobby",
                "inventory": [],
                "move": [],
            },
            "rooms": {"lobby": {"name": "Lobby"}},
            "items": {},
            "flags": {},
            "workbench": {
                "installed_parts": ["chassis_frame", "battery_pack"],
                "required_parts": ["chassis_frame", "battery_pack"],
                "is_ready": True,
            },
            "game_state": {
                "timestamp": "2026-10-26T13:34:05+00:00",
                "duration": _duration("00:10:00"),
                "phase": "ASSEMBLY",
            },
        },
    )

    engine.status()

    rows = _status_rows(rendered["out"])
    assert rows["Assembly"] == "2/2 installed (ready)"


def test_status_visited_shows_last_five(monkeypatch, rendered):
    width = 120
    monkeypatch.setattr(engine, "state", _visited_state(7, width))

    engine.status()

    texts = _out_texts(rendered["out"])
    rows = _status_rows(rendered["out"])
    assert rows["Visited"] == "... Room 3, Room 4, Room 5, Room 6, Room 7"
    visited_line = next(text for text in texts if text.startswith(" Visited:"))
    assert len(visited_line) == width - 1


def test_status_visited_no_ellipsis_at_five(monkeypatch, rendered):
    monkeypatch.setattr(engine, "state", _visited_state(5))

    engine.status()

    rows = _status_rows(rendered["out"])
    assert rows["Visited"] == "Room 1, Room 2, Room 3, Room 4, Room 5"


def test_status_wraps_long_values(monkeypatch, rendered):
    width = 50
    rooms = {
        f"room_{index}": {"name": f"Very Long Room Name {index}"}
        for index in range(1, 7)
    }
    rooms["lobby"] = {"name": "Lobby"}
    items = {
        "chassis": {"name": "Robot Chassis Frame", "is_assembly_part": True},
        "keycard": {"name": "Level-1 Staff Keycard", "is_assembly_part": False},
        "mystery": {"name": "Mystery Component", "is_assembly_part": False},
    }
    monkeypatch.setattr(
        engine,
        "state",
        {
            "terminal_width": width,
            "player": {
                "id": None,
                "name": "guest",
                "current_room": "lobby",
                "inventory": ["chassis", "keycard", "mystery"],
                "move": list(rooms),
            },
            "rooms": rooms,
            "items": items,
            "flags": {},
            "workbench": {
                "installed_parts": [],
                "required_parts": [],
                "is_ready": False,
            },
            "game_state": {
                "timestamp": None,
                "duration": _duration(),
                "phase": "EXPLORATION",
            },
        },
    )

    engine.status()

    texts = _out_texts(rendered["out"])
    assert all(len(text) <= width - 1 for text in texts)

    visited_index = next(
        index for index, text in enumerate(texts) if text.startswith(" Visited:")
    )
    visited_indent = " " * (len(" Visited:") + 1)
    assert texts[visited_index].startswith(" Visited: ...")
    assert texts[visited_index].endswith(",")
    assert texts[visited_index + 1].startswith(visited_indent)
    assert "Very Long Room Name" in texts[visited_index + 1]

    inventory_index = next(
        index for index, text in enumerate(texts) if text.startswith(" Inventory:")
    )
    inventory_indent = " " * (len(" Inventory:") + 1)
    assert any(
        text.startswith(inventory_indent)
        and ("Keycard" in text or "Mystery" in text)
        for text in texts[inventory_index + 1:]
    )


def test_status_wraps_single_long_item(monkeypatch, rendered):
    width = 40
    long_name = "A" * 60
    rooms = {
        "long_room": {"name": long_name},
        "lobby": {"name": "Lobby"},
    }
    monkeypatch.setattr(
        engine,
        "state",
        {
            "terminal_width": width,
            "player": {
                "id": None,
                "name": "guest",
                "current_room": "lobby",
                "inventory": [],
                "move": ["long_room", "lobby"],
            },
            "rooms": rooms,
            "items": {},
            "flags": {},
            "workbench": {
                "installed_parts": [],
                "required_parts": [],
                "is_ready": False,
            },
            "game_state": {
                "timestamp": None,
                "duration": _duration(),
                "phase": "EXPLORATION",
            },
        },
    )

    engine.status()

    texts = _out_texts(rendered["out"])
    assert all(len(text) <= width - 1 for text in texts)
    assert any(text.startswith(" Visited:") for text in texts)
    assert any(
        text.startswith(" " * (len(" Visited:") + 1)) and "A" in text
        for text in texts
    )


def test_print_status_row_wraps_multiline(monkeypatch):
    out_mock = Mock()
    monkeypatch.setattr(engine, "out", out_mock)

    engine._print_status_row("Test", "first line\nsecond line", 40)

    texts = _out_texts(out_mock)
    assert texts[0].startswith(" Test:")
    assert "first line" in texts[0]
    assert texts[1].startswith(" " * (len(" Test:") + 1))
    assert texts[1].strip() == "second line"


def test_inspect_terminal(monkeypatch, inspect_env):
    monkeypatch.setattr(engine, "state", _inspect_state("lobby"))

    engine.inspect({"target": "terminal"})

    inspect_env["render"].assert_called_once_with(text="TERMINAL TEXT", asset="LOGO")


def test_inspect_desk_locked(monkeypatch, inspect_env):
    monkeypatch.setattr(engine, "state", _inspect_state("teachers_room_1"))

    engine.inspect({"target": "desk"})

    inspect_env["render"].assert_called_once_with(text="DESK HINT")


def test_inspect_desk_unlocked(monkeypatch, inspect_env):
    monkeypatch.setattr(
        engine, "state", _inspect_state("teachers_room_1", unlocked=True)
    )

    engine.inspect({"target": "desk"})

    inspect_env["render"].assert_called_once_with(
        text="The desk drawer is open. You already took the keycard."
    )


def test_inspect_workbench(monkeypatch, inspect_env):
    monkeypatch.setattr(engine, "state", _inspect_state("lab_d2_001"))

    engine.inspect({"target": "workbench"})

    inspect_env["workbench"].assert_called_once_with()
    inspect_env["render"].assert_not_called()


def test_inspect_whiteboard(monkeypatch, inspect_env):
    state = _inspect_state("teachers_room_2")
    monkeypatch.setattr(engine, "state", state)

    engine.inspect({"target": "whiteboard"})

    assert state["flags"]["tr2_whiteboard_inspected"] is True
    inspect_env["render"].assert_called_once_with(text="WHITEBOARD TEXT")


def test_inspect_receptionist(monkeypatch, inspect_env):
    monkeypatch.setattr(engine, "state", _inspect_state("front_desk"))

    engine.inspect({"target": "receptionist"})

    inspect_env["render"].assert_called_once_with(text="RECEPTIONIST TEXT")


@pytest.mark.parametrize(
    ("target", "room"),
    [
        pytest.param("door", "lobby", id="unknown-target"),
        pytest.param("terminal", "teachers_room_1", id="wrong-room"),
    ],
)
def test_inspect_unavailable(monkeypatch, inspect_env, target, room):
    monkeypatch.setattr(engine, "state", _inspect_state(room))

    engine.inspect({"target": target})

    inspect_env["render"].assert_called_once_with(
        text="The item you're trying to inspect is unavailable"
    )


def test_use_teachers_room(monkeypatch, use_env):
    monkeypatch.setattr(
        engine,
        "state",
        {"player": {"current_room": "teachers_room_1", "inventory": []}},
    )

    engine.use({"target": "d2084", "indirect": "desk"})

    use_env["desk"].assert_called_once_with("d2084", "desk")


def test_use_lab(monkeypatch, use_env):
    monkeypatch.setattr(
        engine,
        "state",
        {"player": {"current_room": "lab_d2_001", "inventory": []}},
    )

    engine.use({"target": "chassis_frame", "indirect": None})

    use_env["workbench"].assert_called_once_with("chassis_frame")


def test_use_item_not_held(monkeypatch, use_env):
    monkeypatch.setattr(
        engine, "state", {"player": {"current_room": "lobby", "inventory": []}}
    )

    engine.use({"target": "keycard", "indirect": "door"})

    use_env["render"].assert_called_once_with(
        text="You are currently do not have 'keycard' in your inventory."
    )


def test_use_item_cannot_use(monkeypatch, use_env):
    monkeypatch.setattr(
        engine,
        "state",
        {"player": {"current_room": "lobby", "inventory": ["keycard"]}},
    )

    engine.use({"target": "keycard", "indirect": "door"})

    use_env["render"].assert_called_once_with(
        text="You cannot use that keycard on door."
    )


def test_take_missing(monkeypatch, item_env):
    monkeypatch.setattr(
        engine,
        "state",
        {
            "player": {"current_room": "lobby", "inventory": []},
            "rooms": {"lobby": {"items": []}},
        },
    )

    engine.take({"target": "battery"})

    item_env.assert_called_once_with(text="There is no 'battery' here.")


def test_take_success(monkeypatch, item_env):
    state = {
        "player": {"current_room": "lobby", "inventory": []},
        "rooms": {"lobby": {"items": ["battery"]}},
        "items": {"battery": {"name": "High-Capacity Battery Pack"}},
    }
    monkeypatch.setattr(engine, "state", state)

    engine.take({"target": "battery"})

    assert state["rooms"]["lobby"]["items"] == []
    assert state["player"]["inventory"] == ["battery"]
    item_env.assert_called_once_with("You picked up High-Capacity Battery Pack")


def test_drop_item_not_held(monkeypatch, item_env):
    state = {
        "player": {"current_room": "lobby", "inventory": []},
        "rooms": {"lobby": {"items": []}},
        "items": {"battery": {"name": "High-Capacity Battery Pack"}},
    }
    monkeypatch.setattr(engine, "state", state)

    engine.drop({"target": "battery"})

    assert state["rooms"]["lobby"]["items"] == []
    item_env.assert_called_once_with(
        text="You currently do not have 'High-Capacity Battery Pack' here."
    )


def test_drop_success(monkeypatch, item_env):
    state = {
        "player": {"current_room": "lobby", "inventory": ["battery"]},
        "rooms": {"lobby": {"name": "Lobby", "items": []}},
        "items": {"battery": {"name": "High-Capacity Battery Pack"}},
    }
    monkeypatch.setattr(engine, "state", state)

    engine.drop({"target": "battery"})

    assert state["player"]["inventory"] == []
    assert state["rooms"]["lobby"]["items"] == ["battery"]
    item_env.assert_called_once_with(
        "You dropped High-Capacity Battery Pack in Lobby"
    )


def test_command_quit(monkeypatch, command_env):
    state = {"running": True, "terminal_width": 80}
    out = Mock()
    monkeypatch.setattr(engine, "state", state)
    monkeypatch.setattr(engine, "out", out)
    monkeypatch.setattr(engine, "colorize", lambda text=None, color_code=None: text)

    engine.commands("quit", {})

    assert state["running"] is False
    command_env["status"].assert_called_once_with()
    out.assert_called_once_with("Goodbye. see you again soon".center(80))


def test_command_help(command_env):
    engine.commands("help", {})

    command_env["helper"].assert_called_once_with()


def test_command_scoreboard(command_env):
    engine.commands("scoreboard", {})

    command_env["scoreboard"].assert_called_once_with()


def test_command_status(command_env):
    engine.commands("status", {})

    command_env["status"].assert_called_once_with()


def test_command_inventory(command_env):
    engine.commands("inventory", {})

    command_env["inventory"].assert_called_once_with()


def test_command_use(command_env):
    details = {"target": "keycard", "indirect": "door"}

    engine.commands("use", details)

    command_env["use"].assert_called_once_with(details)


@pytest.mark.parametrize(
    "details",
    [
        pytest.param({"target": "slot2.json"}, id="explicit"),
        pytest.param({"target": None}, id="default-none"),
    ],
)
def test_command_save(command_env, details):
    engine.commands("save", details)

    command_env["save"].assert_called_once_with(details)


def test_command_register(command_env):
    details = {"target": "alice"}

    engine.commands("register", details)

    command_env["register"].assert_called_once_with(details)


def test_command_login(command_env):
    details = {"target": "alice"}

    engine.commands("login", details)

    command_env["login"].assert_called_once_with(details)


def test_command_logout(command_env):
    engine.commands("logout", {})

    command_env["logout"].assert_called_once_with()


def test_command_load(command_env):
    details = {"target": "slot1"}

    engine.commands("load", details)

    command_env["load"].assert_called_once_with(details)


def test_command_saves(command_env):
    engine.commands("saves", {})

    command_env["list_saves"].assert_called_once_with()


def test_command_inspect(command_env):
    details = {"target": "desk"}

    engine.commands("inspect", details)

    command_env["inspect"].assert_called_once_with(details)


def test_command_look(command_env):
    engine.commands("look", {})

    command_env["render"].assert_called_once_with()


@pytest.mark.parametrize(
    "details",
    [
        pytest.param({"target": "battery"}, id="with-target"),
        pytest.param({}, id="empty"),
    ],
)
def test_command_take(command_env, details):
    engine.commands("take", details)

    command_env["take"].assert_called_once_with(details)


def test_command_drop(command_env):
    details = {"target": "battery"}

    engine.commands("drop", details)

    command_env["drop"].assert_called_once_with(details)


@pytest.mark.parametrize(
    "details",
    [
        pytest.param({"target": "north"}, id="with-target"),
        pytest.param({}, id="empty"),
    ],
)
def test_command_go(command_env, details):
    engine.commands("go", details)

    command_env["move"].assert_called_once_with(details)


def test_command_restart(command_env):
    engine.commands("restart", {})

    command_env["restart"].assert_called_once_with()


def test_command_unknown_verb_is_ignored(command_env):
    engine.commands("fly", {})

    for mock in command_env.values():
        mock.assert_not_called()


@pytest.mark.parametrize(
    ("phase", "expected_handler"),
    [
        pytest.param("EXPLORATION", "exploration", id="exploration"),
        pytest.param("ASSEMBLY", "assembly", id="assembly"),
        pytest.param("CHAT", "chat", id="chat"),
        pytest.param("UNKNOWN", "exploration", id="else-fallback"),
    ],
)
def test_run_dispatches_phase(monkeypatch, phase, expected_handler):
    state = {"running": True, "game_state": {"phase": phase}}
    monkeypatch.setattr(engine, "state", state)

    exploration_mock = Mock()
    assembly_mock = Mock()
    chat_mock = Mock()
    monkeypatch.setattr(phase_module, "exploration", exploration_mock)
    monkeypatch.setattr(phase_module, "assembly", assembly_mock)
    monkeypatch.setattr(phase_module, "chat", chat_mock)

    spawn_mock = Mock()
    monkeypatch.setattr(engine, "spawn", spawn_mock)

    auto_mock = Mock(side_effect=lambda: state.update({"running": False}))
    monkeypatch.setattr(engine, "auto", auto_mock)

    engine.run()

    spawn_mock.assert_called_once_with()
    auto_mock.assert_called_once_with()

    handlers = {
        "exploration": exploration_mock,
        "assembly": assembly_mock,
        "chat": chat_mock,
    }
    for name, handler in handlers.items():
        if name == expected_handler:
            handler.assert_called_once_with()
        else:
            handler.assert_not_called()


def _render_text(render_mock):
    call = render_mock.call_args
    return call.args[0] if call.args else call.kwargs["text"]


@pytest.fixture
def register_env(monkeypatch):
    mocks = {
        "render": Mock(),
        "get_user": Mock(return_value=None),
        "create_user": Mock(return_value=7),
    }
    monkeypatch.setattr(engine, "render", mocks["render"])
    monkeypatch.setattr(engine, "get_user", mocks["get_user"])
    monkeypatch.setattr(engine, "create_user", mocks["create_user"])
    monkeypatch.setattr(engine, "colorize", lambda text=None, color_code=None: text)
    return mocks


def test_register_requires_front_desk(monkeypatch, register_env):
    monkeypatch.setattr(engine, "state", {"player": {"current_room": "lobby"}})

    engine.register({"target": "alice"})

    register_env["get_user"].assert_not_called()
    register_env["create_user"].assert_not_called()
    assert "front desk" in _render_text(register_env["render"]).lower()


def test_register_creates_profile(monkeypatch, register_env):
    state = {"player": {"current_room": "front_desk"}}
    monkeypatch.setattr(engine, "state", state)

    engine.register({"target": "alice"})

    register_env["get_user"].assert_called_once_with("alice")
    register_env["create_user"].assert_called_once_with("alice")
    assert state["player"]["name"] == "alice"
    assert state["player"]["id"] == 7
    assert "successfully registered" in _render_text(register_env["render"]).lower()


def test_register_rejects_existing_name(monkeypatch, register_env):
    register_env["get_user"].return_value = 1
    monkeypatch.setattr(engine, "state", {"player": {"current_room": "front_desk"}})

    engine.register({"target": "alice"})

    register_env["create_user"].assert_not_called()
    assert "already taken" in _render_text(register_env["render"]).lower()


def test_register_reports_db_error(monkeypatch, register_env):
    register_env["create_user"].side_effect = Exception("boom")
    monkeypatch.setattr(engine, "state", {"player": {"current_room": "front_desk"}})

    engine.register({"target": "alice"})

    assert "boom" in _render_text(register_env["render"])


@pytest.fixture
def login_env(monkeypatch):
    mocks = {
        "render": Mock(),
        "get_user": Mock(return_value=None),
    }
    monkeypatch.setattr(engine, "render", mocks["render"])
    monkeypatch.setattr(engine, "get_user", mocks["get_user"])
    monkeypatch.setattr(engine, "colorize", lambda text=None, color_code=None: text)
    return mocks


@pytest.fixture
def logout_env(monkeypatch):
    render = Mock()
    monkeypatch.setattr(engine, "render", render)
    monkeypatch.setattr(engine, "colorize", lambda text=None, color_code=None: text)
    return render


def test_login_requires_front_desk(monkeypatch, login_env):
    monkeypatch.setattr(engine, "state", {"player": {"current_room": "lobby"}})

    engine.login({"target": "alice"})

    login_env["get_user"].assert_not_called()
    assert "front desk" in _render_text(login_env["render"]).lower()


def test_login_without_name(monkeypatch, login_env):
    monkeypatch.setattr(engine, "state", {"player": {"current_room": "front_desk"}})

    engine.login({"target": None})

    login_env["get_user"].assert_not_called()
    assert "enter a name" in _render_text(login_env["render"]).lower()


def test_login_unknown_user(monkeypatch, login_env):
    monkeypatch.setattr(engine, "state", {"player": {"current_room": "front_desk"}})

    engine.login({"target": "alice"})

    login_env["get_user"].assert_called_once_with("alice")
    assert "does not exist" in _render_text(login_env["render"]).lower()


def test_login_success(monkeypatch, login_env):
    login_env["get_user"].return_value = {"id": 7, "name": "alice"}
    state = {"player": {"current_room": "front_desk"}}
    monkeypatch.setattr(engine, "state", state)

    engine.login({"target": "alice"})

    assert state["player"]["name"] == "alice"
    assert state["player"]["id"] == 7
    assert "logged in" in _render_text(login_env["render"]).lower()


def test_logout_requires_front_desk(monkeypatch, logout_env):
    state = {
        "player": {"current_room": "lobby", "id": 7, "name": "alice"},
    }
    monkeypatch.setattr(engine, "state", state)

    engine.logout()

    logout_env.assert_called_once()
    assert state["player"]["id"] == 7
    assert state["player"]["name"] == "alice"
    assert "front desk" in _render_text(logout_env).lower()


def test_logout_requires_login(monkeypatch, logout_env):
    state = {
        "player": {"current_room": "front_desk", "id": None, "name": "guest"},
    }
    monkeypatch.setattr(engine, "state", state)

    engine.logout()

    logout_env.assert_called_once()
    assert state["player"]["id"] is None
    assert state["player"]["name"] == "guest"
    assert "not logged in" in _render_text(logout_env).lower()


def test_logout_success(monkeypatch, logout_env):
    state = {
        "player": {
            "current_room": "front_desk",
            "id": 7,
            "name": "alice",
            "inventory": ["keycard_lvl1"],
        },
    }
    monkeypatch.setattr(engine, "state", state)

    engine.logout()

    logout_env.assert_called_once()
    assert state["player"]["id"] is None
    assert state["player"]["name"] == "guest"
    assert state["player"]["inventory"] == ["keycard_lvl1"]
    assert "logged out from alice" in _render_text(logout_env).lower()


def test_restart_resets_state_but_keeps_player(monkeypatch, tmp_path):
    default_path = tmp_path / "default_state.json"
    default_path.write_text(
        json.dumps(
            {
                "player": {"id": None, "name": "guest", "current_room": "lobby"},
                "rooms": {"lobby": {}},
                "game_state": {
                    "timestamp": "2020-01-01T00:00:00+00:00",
                    "duration": _duration(),
                },
            }
        ),
        encoding="utf-8",
    )
    game_state = {
        "player": {"id": 3, "name": "polaris", "current_room": "lab"},
        "rooms": {"lab": {}},
    }
    render = Mock()
    monkeypatch.setattr(engine, "state", game_state)
    monkeypatch.setattr(engine, "DEFAULT_GAME_STATE_PATH", default_path)
    monkeypatch.setattr(engine, "render", render)
    monkeypatch.setattr(engine, "colorize", lambda text=None, color_code=None: text)

    engine.restart()

    assert engine.state is game_state
    assert game_state["player"]["name"] == "polaris"
    assert game_state["player"]["id"] == 3
    assert game_state["player"]["current_room"] == "lobby"
    assert game_state["rooms"] == {"lobby": {}}
    duration = game_state["game_state"]["duration"]
    assert duration["value"] == "00:00:00"
    assert duration["pause"] is False
    assert duration["last_write"] is not None
    assert (
        game_state["game_state"]["timestamp"]
        != "2020-01-01T00:00:00+00:00"
    )
    render.assert_called_once_with(text="New game!")
