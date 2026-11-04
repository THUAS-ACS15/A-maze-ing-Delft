import copy
import json
import time

import pytest
import builtins

from unittest.mock import Mock

import db
import src.engine as engine
import src.state as state_module
from src import room
from src.state import DEFAULT_GAME_STATE_PATH
from src import parser
from src.rooms import front_desk
from src.rooms import lobby
from src.rooms import teachers_room_1
from src.rooms import teachers_room_2
from src.rooms import teachers_room_4
from src.rooms import lab_d2_001
from src import phase
from src.utils.shell import VirtualShell

DESK_CODE = "D2084"
REWARD = "keycard_lvl1"

REQUIRED_PARTS = ["chassis_frame", "battery_pack"]
ITEM_NAMES = {
    "chassis_frame": "Robot Chassis Frame",
    "battery_pack": "High-Capacity Battery Pack",
    "keycard_lvl1": "Level-1 Staff Keycard",
}
WIFI_PASSWORD = "Tr0janH0rse!"

BASE_STATE = {
    "enable_colors": False,
    "terminal_width": 20,
    "player": {"current_room": "lab", "name": "guest"},
    "game_state": {
        "phase": "EXPLORATION",
        "duration": {"last_write": None, "value": "00:00:00", "pause": False},
    },
    "rooms": {
        "lab": {
            "name": "Lab",
            "description": "A test lab.",
            "exits": {"east": "hall"},
            "items": [],
            "interactables": {},
        },
        "hall": {"name": "Hall"},
    },
    "items": {},
}

DIRECTIONS = {"north": "north", "south": "south", "east": "east", "west": "west"}

@pytest.fixture
def db_table_names():
    def _table_names(conn):
        return {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    return _table_names

@pytest.fixture
def state():
    with open(DEFAULT_GAME_STATE_PATH) as df:
        return json.load(df)

@pytest.fixture
def database(monkeypatch, tmp_path):
    """Point the db module at a throwaway database and create the schema."""
    db_path = tmp_path / "game.db"
    monkeypatch.setattr(db, "DATABASE_PATH", db_path)
    db.init()
    return db_path


@pytest.fixture
def room_state(monkeypatch):
    """Patch both state bindings that ``render()`` relies on.

    ``room.render()`` reads the module-level ``room.state`` import, while the
    ``display`` helpers resolve ``src.state.state`` freshly on each call.
    Patching both to the same dict keeps them consistent.
    """
    state = copy.deepcopy(BASE_STATE)
    monkeypatch.setattr(room, "state", state)
    monkeypatch.setattr(state_module, "state", state)
    return state

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


@pytest.fixture
def shell():
    return VirtualShell(
        {
            "etc": {"hostname": "teacher-pc"},
            "home": {
                "teacher": {
                    "Documents": {
                        "grades.csv": "grades",
                        "notes.md": "notes",
                        ".hidden.txt": "hidden",
                    },
                    "Downloads": {"manual.txt": "manual"},
                    ".secret": {"super_secret_file.txt": "the key"},
                    ".bashrc": "export PS1='$ '",
                    "README.txt": "read me",
                    "my notes.txt": "spaced",
                }
            },
            "var": {"log": {"nixos.log": "log"}},
        }
    )

@pytest.fixture
def move_env(monkeypatch):
    """Patch move()'s locally-imported dependencies."""
    render_mock = Mock()
    monkeypatch.setattr(
        state_module, "colorize", lambda text=None, color_code=None: text
    )
    monkeypatch.setattr(room, "render", render_mock)
    monkeypatch.setattr(parser, "resolve_room_target", lambda raw: raw)
    monkeypatch.setattr(parser, "ROOM_ALIASES", DIRECTIONS)
    return render_mock

@pytest.fixture
def desk(monkeypatch):
    state = {
        "rooms": {
            "teachers_room_1": {
                "interactables": {"desk": {"code": DESK_CODE, "reward": REWARD}}
            }
        },
        "flags": {"tr1_desk_unlocked": False},
        "player": {"inventory": []},
    }
    render_mock = Mock()
    monkeypatch.setattr(teachers_room_1, "state", state)
    monkeypatch.setattr(teachers_room_1, "render", render_mock)
    monkeypatch.setattr(
        teachers_room_1, "colorize", lambda text, color_code=None: text
    )
    return {"state": state, "render": render_mock}

@pytest.fixture
def terminal_state(monkeypatch):
    state = {
        "player": {"inventory": []},
        "flags": {"tr4_secret_key_copied": False},
        "items": {"secret_key": {"name": "Secret Key"}},
        "game_state": {
            "duration": {"pause": False, "last_write": None, "value": "00:00:00"},
            "phase": "EXPLORATION",
        },
        "workbench": {"is_ready": False},
        "rooms": {
            "teachers_room_4": {"description": "The senior faculty office."}
        },
    }
    monkeypatch.setattr(teachers_room_4, "state", state)
    return state

@pytest.fixture
def mocks(monkeypatch):
    """Replace every dependency phase.py resolves at module level."""
    prompt = Mock(return_value="raw input")
    parse = Mock(return_value=("GO", {}))
    commands = Mock()
    clear = Mock()
    render = Mock()
    header = Mock()
    out = Mock()
    respond = Mock()
    workbench = Mock()
    activate = Mock()

    monkeypatch.setattr(phase, "prompt", prompt)
    monkeypatch.setattr(phase, "parse", parse)
    monkeypatch.setattr(phase, "commands", commands)
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
        "commands": commands,
        "clear": clear,
        "render": render,
        "header": header,
        "out": out,
        "respond": respond,
        "workbench": workbench,
        "activate": activate,
        "state": state,
    }

@pytest.fixture
def wb_rendered(monkeypatch):
    """Patch workbench()'s rendering helpers."""
    out_mock = Mock()
    draw_mock = Mock()
    monkeypatch.setattr(lab_d2_001, "out", out_mock)
    monkeypatch.setattr(lab_d2_001, "draw_line", draw_mock)
    monkeypatch.setattr(lab_d2_001, "colorize", lambda text, color_code=None: text)
    return {"out": out_mock, "draw_line": draw_mock}


@pytest.fixture
def assembly(monkeypatch):
    """Patch the workbench dependency used by use_on_workbench()."""
    workbench_mock = Mock()
    monkeypatch.setattr(lab_d2_001, "workbench", workbench_mock)
    monkeypatch.setattr(lab_d2_001, "colorize", lambda text, color_code=None: text)
    return {"workbench": workbench_mock}


@pytest.fixture
def activate_env(monkeypatch):
    """Patch activate()'s dependencies."""
    workbench_mock = Mock()
    prompt_mock = Mock()
    clear_mock = Mock()
    render_mock = Mock()
    time_mock = Mock()
    scoreboard_mock = Mock()

    monkeypatch.setattr(lab_d2_001, "workbench", workbench_mock)
    monkeypatch.setattr(lab_d2_001, "colorize", lambda text, color_code=None: text)
    monkeypatch.setattr(lab_d2_001, "clear", clear_mock)
    monkeypatch.setattr(lab_d2_001, "render", render_mock)
    monkeypatch.setattr(lab_d2_001, "time", time_mock)
    monkeypatch.setattr(lab_d2_001, "create_scoreboard_entry", scoreboard_mock)
    monkeypatch.setattr(engine, "prompt", prompt_mock)

    return {
        "workbench": workbench_mock,
        "prompt": prompt_mock,
        "clear": clear_mock,
        "render": render_mock,
        "time": time_mock,
        "create_scoreboard_entry": scoreboard_mock,
    }

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

@pytest.fixture
def en_rendered(monkeypatch):
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
    computer_mock = Mock()
    monkeypatch.setattr(engine, "render", render_mock)
    monkeypatch.setattr(engine, "workbench", workbench_mock)
    monkeypatch.setattr(engine, "inspect_computer", computer_mock)
    monkeypatch.setattr(engine, "colorize", lambda text=None, color_code=None: text)
    for module in (front_desk, lobby, teachers_room_1, teachers_room_2):
        monkeypatch.setattr(module, "render", render_mock)
    monkeypatch.setattr(
        teachers_room_1, "colorize", lambda text, color_code=None: text
    )
    monkeypatch.setattr(lobby, "logo", "LOGO")
    monkeypatch.setattr("src.assets.logo.logo", "LOGO")
    return {
        "render": render_mock,
        "workbench": workbench_mock,
        "computer": computer_mock,
    }


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


@pytest.fixture
def block_rich_import():
    """Return a helper that simulates rich not being installed."""

    def _block(monkeypatch):
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "rich.console":
                raise ModuleNotFoundError("No module named 'rich.console'")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)

    return _block


def _out_texts(out_mock):
    return [call.args[0] for call in out_mock.call_args_list if call.args]


@pytest.fixture
def out_texts():
    return _out_texts


def _status_rows(out_mock):
    rows = {}
    for text in _out_texts(out_mock):
        label, separator, value = text.strip().partition(":")
        if separator and not label.startswith("•"):
            rows[label] = value.strip()
    return rows


@pytest.fixture
def status_rows():
    return _status_rows


def _duration(value="00:00:00"):
    return {"last_write": None, "value": value, "pause": False}


@pytest.fixture
def duration():
    return _duration


@pytest.fixture
def status_full_state():
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


def _visited_state(count, width=120):
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


@pytest.fixture
def visited_state():
    return _visited_state


def _inspect_state(current_room, unlocked=False):
    return {
        "player": {"current_room": current_room},
        "rooms": {
            "lobby": {"interactables": {"terminal": "TERMINAL TEXT"}},
            "teachers_room_1": {"interactables": {"desk": {"hint": "DESK HINT"}}},
            "teachers_room_2": {"interactables": {"whiteboard": "WHITEBOARD TEXT"}},
            "front_desk": {"interactables": {"receptionist": "RECEPTIONIST TEXT"}},
            "teachers_room_4": {"interactables": {"computer": "NIX"}},
            "lab_d2_001": {},
        },
        "flags": {
            "tr1_desk_unlocked": unlocked,
            "tr2_whiteboard_inspected": False,
        },
    }


@pytest.fixture
def inspect_state():
    return _inspect_state


@pytest.fixture
def set_inspect_state(monkeypatch, inspect_state):
    """Return a helper that patches every state binding used by ``engine.inspect()``."""

    def _set(current_room, unlocked=False):
        state = inspect_state(current_room, unlocked)
        monkeypatch.setattr(engine, "state", state)
        for module in (front_desk, lobby, teachers_room_1, teachers_room_2):
            monkeypatch.setattr(module, "state", state)
        return state

    return _set


def _render_text(render_mock):
    call = render_mock.call_args
    return call.args[0] if call.args else call.kwargs["text"]


@pytest.fixture
def render_text():
    return _render_text


@pytest.fixture
def make_lab_state():
    return _make_state


@pytest.fixture
def wb_messages():
    return _wb_messages


@pytest.fixture
def desk_code():
    return DESK_CODE


@pytest.fixture
def reward():
    return REWARD


@pytest.fixture
def required_parts():
    return REQUIRED_PARTS


@pytest.fixture
def wifi_password():
    return WIFI_PASSWORD


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


def _make_state(
    installed,
    inventory=None,
    phase="EXPLORATION",
    robot_name="Jarvis",
    player_id=1,
    room_count=2,
    total_time="0:00:00",
    assembly_time="0:00:00",
):
    return {
        "workbench": {
            "installed_parts": list(installed),
            "required_parts": list(REQUIRED_PARTS),
            "is_ready": False,
        },
        "items": {part: {"name": name} for part, name in ITEM_NAMES.items()},
        "player": {
            "id": player_id,
            "inventory": list(inventory) if inventory is not None else [],
        },
        "rooms": {f"room_{index}": {} for index in range(room_count)},
        "game_state": {
            "phase": phase,
            "duration": {
                "last_write": None,
                "value": total_time,
                "pause": False,
            },
            "phases": {
                "assembly": {
                    "wifi_password": WIFI_PASSWORD,
                    "duration": {
                        "last_write": None,
                        "value": assembly_time,
                        "pause": False,
                    },
                },
                "chat": {"robot": {"name": robot_name}},
            },
        },
    }


def _wb_message(call):
    """Extract the message from a workbench() call (positional or text=)."""
    if call.args:
        return call.args[0]
    return call.kwargs.get("text")


def _wb_messages(workbench_mock):
    return [_wb_message(call) for call in workbench_mock.call_args_list]
