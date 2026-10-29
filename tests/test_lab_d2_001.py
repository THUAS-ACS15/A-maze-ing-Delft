"""Tests for ``src/rooms/lab_d2_001.py``."""

from unittest.mock import Mock

import pytest

import src.engine as engine
from src.rooms import lab_d2_001

REQUIRED_PARTS = ["chassis_frame", "battery_pack"]
ITEM_NAMES = {
    "chassis_frame": "Robot Chassis Frame",
    "battery_pack": "High-Capacity Battery Pack",
    "keycard_lvl1": "Level-1 Staff Keycard",
}
WIFI_PASSWORD = "Tr0janH0rse!"


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


def _out_texts(out_mock):
    return [call.args[0] for call in out_mock.call_args_list if call.args]


def _wb_message(call):
    """Extract the message from a workbench() call (positional or text=)."""
    if call.args:
        return call.args[0]
    return call.kwargs.get("text")


def _wb_messages(workbench_mock):
    return [_wb_message(call) for call in workbench_mock.call_args_list]


@pytest.fixture
def rendered(monkeypatch):
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


def test_workbench_status_labels(monkeypatch, rendered):
    monkeypatch.setattr(
        lab_d2_001, "state", _make_state(installed=["chassis_frame"])
    )

    lab_d2_001.workbench()

    assert rendered["draw_line"].call_count == 2
    texts = _out_texts(rendered["out"])
    assert "Progress: 1 / 2 components installed.\n" in texts
    assert " [ INSTALLED ] - Robot Chassis Frame" in texts
    assert " [ MISSING   ] - High-Capacity Battery Pack" in texts
    assert "Locate remaining 1 part(s) to complete assembly." in texts


def test_workbench_incomplete_with_text(monkeypatch, rendered, capsys):
    monkeypatch.setattr(lab_d2_001, "state", _make_state(installed=[]))

    lab_d2_001.workbench(text="custom hint")

    assert capsys.readouterr().out == "custom hint\n"
    assert "Locate remaining 2 part(s) to complete assembly." in _out_texts(
        rendered["out"]
    )


def test_workbench_complete_default_command(monkeypatch, rendered):
    monkeypatch.setattr(
        lab_d2_001, "state", _make_state(installed=REQUIRED_PARTS)
    )

    lab_d2_001.workbench()

    texts = _out_texts(rendered["out"])
    assert ">> ALL CORE COMPONENTS INSTALLED <<" in texts
    assert "Type 'activate' or 'power on' to start the neural link." in texts


def test_workbench_complete_custom_command(monkeypatch, rendered):
    monkeypatch.setattr(
        lab_d2_001, "state", _make_state(installed=REQUIRED_PARTS)
    )

    lab_d2_001.workbench(text="custom command")

    texts = _out_texts(rendered["out"])
    assert ">> ALL CORE COMPONENTS INSTALLED <<" in texts
    assert "custom command" in texts
    assert "Type 'activate' or 'power on' to start the neural link." not in texts


def test_workbench_complete_but_chat_phase(monkeypatch, rendered):
    monkeypatch.setattr(
        lab_d2_001, "state", _make_state(installed=REQUIRED_PARTS, phase="CHAT")
    )

    lab_d2_001.workbench()

    texts = _out_texts(rendered["out"])
    assert ">> ALL CORE COMPONENTS INSTALLED <<" not in texts
    assert "Locate remaining 0 part(s) to complete assembly." in texts


def test_use_unknown_item(monkeypatch, assembly):
    monkeypatch.setattr(lab_d2_001, "state", _make_state(installed=[]))

    lab_d2_001.use_on_workbench("nonexistent")

    assert _wb_messages(assembly["workbench"]) == [
        "'nonexistent' is not a workbench component."
    ]


def test_use_item_not_in_inventory(monkeypatch, assembly):
    monkeypatch.setattr(lab_d2_001, "state", _make_state(installed=[]))

    lab_d2_001.use_on_workbench("chassis_frame")

    assert _wb_messages(assembly["workbench"]) == [
        "You currently do not have Robot Chassis Frame in your inventory."
    ]


def test_use_non_required_item(monkeypatch, assembly):
    monkeypatch.setattr(
        lab_d2_001, "state", _make_state(installed=[], inventory=["keycard_lvl1"])
    )

    lab_d2_001.use_on_workbench("keycard_lvl1")

    assert _wb_messages(assembly["workbench"]) == [
        "'Level-1 Staff Keycard' is not a workbench component."
    ]


def test_use_already_installed(monkeypatch, assembly):
    monkeypatch.setattr(
        lab_d2_001,
        "state",
        _make_state(installed=["chassis_frame"], inventory=["chassis_frame"]),
    )

    lab_d2_001.use_on_workbench("chassis_frame")

    assert _wb_messages(assembly["workbench"]) == [
        "'Robot Chassis Frame' is already installed."
    ]


def test_use_installs_part_not_complete(monkeypatch, assembly):
    state = _make_state(installed=[], inventory=["chassis_frame"])
    monkeypatch.setattr(lab_d2_001, "state", state)

    lab_d2_001.use_on_workbench("chassis_frame")

    assert _wb_messages(assembly["workbench"]) == [
        "Robot Chassis Frame installed (1/2)."
    ]
    assert state["player"]["inventory"] == []
    assert state["workbench"]["installed_parts"] == ["chassis_frame"]
    assert state["workbench"]["is_ready"] is False
    assert state["game_state"]["phase"] == "EXPLORATION"


def test_use_installs_last_part_completes(monkeypatch, assembly):
    state = _make_state(installed=["chassis_frame"], inventory=["battery_pack"])
    monkeypatch.setattr(lab_d2_001, "state", state)

    lab_d2_001.use_on_workbench("battery_pack")

    messages = _wb_messages(assembly["workbench"])
    assert len(messages) == 1
    assert "ALL COMPONENTS INSTALLED" in messages[0]
    assert state["player"]["inventory"] == []
    assert state["workbench"]["installed_parts"] == [
        "chassis_frame",
        "battery_pack",
    ]
    assert state["workbench"]["is_ready"] is True
    assert state["game_state"]["phase"] == "ASSEMBLY"


def test_activate_incomplete(monkeypatch, activate_env):
    monkeypatch.setattr(lab_d2_001, "state", _make_state(installed=[]))

    lab_d2_001.activate()

    assert _wb_messages(activate_env["workbench"]) == [
        "Assembly incomplete. 2 part(s) missing."
    ]
    activate_env["prompt"].assert_not_called()
    activate_env["clear"].assert_not_called()


def test_activate_wrong_password(monkeypatch, activate_env):
    monkeypatch.setattr(
        lab_d2_001, "state", _make_state(installed=REQUIRED_PARTS)
    )
    activate_env["prompt"].return_value = "wrong-password"

    lab_d2_001.activate()

    assert _wb_messages(activate_env["workbench"]) == [
        "Enter wifi password to continue.",
        "Invalid wifi credentials.",
    ]
    activate_env["prompt"].assert_called_once_with()
    activate_env["clear"].assert_called_once()


@pytest.mark.parametrize(
    ("name_input", "expected_name"),
    [
        pytest.param("", "Jarvis", id="empty-keeps-default"),
        pytest.param("   ", "Jarvis", id="whitespace-keeps-default"),
        pytest.param("Bob", "Bob", id="simple-name"),
        pytest.param("  Bob  ", "Bob", id="stripped-name"),
    ],
)
def test_activate_success(monkeypatch, activate_env, name_input, expected_name):
    state = _make_state(installed=REQUIRED_PARTS)
    monkeypatch.setattr(lab_d2_001, "state", state)
    activate_env["prompt"].side_effect = [WIFI_PASSWORD, name_input]

    lab_d2_001.activate()

    assert state["game_state"]["phase"] == "CHAT"
    assert state["game_state"]["phases"]["chat"]["robot"]["name"] == expected_name

    assert activate_env["prompt"].call_count == 2
    assert activate_env["clear"].call_count == 2
    activate_env["render"].assert_called_once_with(
        f"INITIALIZING {expected_name.upper()}..."
    )
    activate_env["time"].sleep.assert_called_once_with(2)

    messages = _wb_messages(activate_env["workbench"])
    assert messages[0] == "Enter wifi password to continue."
    assert messages[1] == "Give your robot a name. Default name is Jarvis."


def test_activate_records_weighted_score(monkeypatch, activate_env):
    state = _make_state(
        installed=REQUIRED_PARTS,
        player_id=7,
        room_count=5,
        total_time="0:30:00",
        assembly_time="0:05:00",
    )
    monkeypatch.setattr(lab_d2_001, "state", state)
    activate_env["prompt"].side_effect = [WIFI_PASSWORD, "Bob"]

    lab_d2_001.activate()

    activate_env["create_scoreboard_entry"].assert_called_once_with(
        user_id=7,
        score=680,
        avg_room_time="0:05:00",
        exploration_time="0:25:00",
        assembly_time="0:05:00",
    )


def test_activate_skips_scoreboard_for_guest(monkeypatch, activate_env):
    state = _make_state(
        installed=REQUIRED_PARTS,
        player_id=None,
        total_time="0:10:00",
        assembly_time="0:01:00",
    )
    monkeypatch.setattr(lab_d2_001, "state", state)
    activate_env["prompt"].side_effect = [WIFI_PASSWORD, "Bob"]

    lab_d2_001.activate()

    activate_env["create_scoreboard_entry"].assert_not_called()
