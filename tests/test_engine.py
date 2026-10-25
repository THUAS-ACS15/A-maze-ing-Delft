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
    draw_mock = Mock()
    monkeypatch.setattr(engine, "out", out_mock)
    monkeypatch.setattr(engine, "draw_line", draw_mock)
    monkeypatch.setattr(engine, "colorize", lambda text=None, color_code=None: text)
    return {"out": out_mock, "draw_line": draw_mock}


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
def take_env(monkeypatch):
    render_mock = Mock()
    monkeypatch.setattr(engine, "render", render_mock)
    monkeypatch.setattr(engine, "colorize", lambda text=None, color_code=None: text)
    return render_mock


@pytest.fixture
def command_env(monkeypatch):
    mocks = {
        "render": Mock(),
        "helper": Mock(),
        "inventory": Mock(),
        "use": Mock(),
        "register": Mock(),
        "login": Mock(),
        "save": Mock(),
        "list_saves": Mock(),
        "load": Mock(),
        "inspect": Mock(),
        "take": Mock(),
        "move": Mock(),
        "restart": Mock(),
    }
    for name, mock in mocks.items():
        monkeypatch.setattr(engine, name, mock)
    return mocks


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
            "game_state": {"phase": "EXPLORATION", "duration": "00:00:00"},
            "player": {"inventory": []},
        },
    )

    engine.inventory()

    assert rendered["draw_line"].call_count == 2
    assert "Your inventory is currently empty." in _out_texts(rendered["out"])


def test_inventory_populated(monkeypatch, rendered):
    monkeypatch.setattr(
        engine,
        "state",
        {
            "game_state": {"phase": "EXPLORATION", "duration": "00:05:00"},
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
    monkeypatch.setattr(engine, "state", {"game_state": {"phase": phase}})

    engine.helper()

    texts = _out_texts(rendered["out"])
    assert texts[0] == "Available Commands:"
    assert any("[Movement]" in text for text in texts)
    assert bool([text for text in texts if "[Assembly]" in text]) is assembly_visible


def test_helper_rich_path(monkeypatch):
    console_cls = Mock()
    table_cls = Mock()
    monkeypatch.setattr("rich.console.Console", console_cls)
    monkeypatch.setattr("rich.table.Table", table_cls)
    monkeypatch.setattr(engine, "help_commands", HELP_GROUPS)
    monkeypatch.setattr(engine, "state", {"game_state": {"phase": "EXPLORATION"}})

    engine.helper()

    console_cls.return_value.print.assert_called_once_with(table_cls.return_value)
    table_cls.return_value.add_row.assert_called_once_with("go", "Move", "go north")


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


def test_take_missing(monkeypatch, take_env):
    monkeypatch.setattr(
        engine,
        "state",
        {
            "player": {"current_room": "lobby", "inventory": []},
            "rooms": {"lobby": {"items": []}},
        },
    )

    engine.take({"target": "battery"})

    take_env.assert_called_once_with(text="There is no 'battery' here.")


def test_take_success(monkeypatch, take_env):
    state = {
        "player": {"current_room": "lobby", "inventory": []},
        "rooms": {"lobby": {"items": ["battery"]}},
        "items": {"battery": {"name": "High-Capacity Battery Pack"}},
    }
    monkeypatch.setattr(engine, "state", state)

    engine.take({"target": "battery"})

    assert state["rooms"]["lobby"]["items"] == []
    assert state["player"]["inventory"] == ["battery"]
    take_env.assert_called_once_with("You picked up High-Capacity Battery Pack")


def test_command_quit(monkeypatch, command_env):
    state = {"running": True}
    monkeypatch.setattr(engine, "state", state)

    engine.commands("quit", {})

    assert state["running"] is False
    command_env["render"].assert_called_once_with("Goodbye. see you again soon")


def test_command_help(command_env):
    engine.commands("help", {})

    command_env["helper"].assert_called_once_with()


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


def test_restart_resets_state_but_keeps_player(monkeypatch, tmp_path):
    default_path = tmp_path / "default_state.json"
    default_path.write_text(
        json.dumps(
            {
                "player": {"id": None, "name": "guest", "current_room": "lobby"},
                "rooms": {"lobby": {}},
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
    render.assert_called_once_with(text="New game!")
