"""Tests for ``src/rooms/lab_d2_001.py``."""

import pytest

from src.rooms import lab_d2_001

def test_workbench_status_labels(monkeypatch, wb_rendered, make_lab_state, out_texts):
    monkeypatch.setattr(
        lab_d2_001, "state", make_lab_state(installed=["chassis_frame"])
    )

    lab_d2_001.workbench()

    assert wb_rendered["draw_line"].call_count == 2
    texts = out_texts(wb_rendered["out"])
    assert "Progress: 1 / 2 components installed.\n" in texts
    assert " [ INSTALLED ] - Robot Chassis Frame" in texts
    assert " [ MISSING   ] - High-Capacity Battery Pack" in texts
    assert "Locate remaining 1 part(s) to complete assembly." in texts


def test_workbench_incomplete_with_text(monkeypatch, wb_rendered, capsys,
                                        make_lab_state, out_texts):
    monkeypatch.setattr(lab_d2_001, "state", make_lab_state(installed=[]))

    lab_d2_001.workbench(text="custom hint")

    assert capsys.readouterr().out == "custom hint\n"
    assert "Locate remaining 2 part(s) to complete assembly." in out_texts(
        wb_rendered["out"]
    )


def test_workbench_complete_default_command(monkeypatch, wb_rendered,
                                            make_lab_state, required_parts,
                                            out_texts):
    monkeypatch.setattr(
        lab_d2_001, "state", make_lab_state(installed=required_parts)
    )

    lab_d2_001.workbench()

    texts = out_texts(wb_rendered["out"])
    assert ">> ALL CORE COMPONENTS INSTALLED <<" in texts
    assert "Type 'activate' or 'power on' to start the neural link." in texts


def test_workbench_complete_custom_command(monkeypatch, wb_rendered,
                                           make_lab_state, required_parts,
                                           out_texts):
    monkeypatch.setattr(
        lab_d2_001, "state", make_lab_state(installed=required_parts)
    )

    lab_d2_001.workbench(text="custom command")

    texts = out_texts(wb_rendered["out"])
    assert ">> ALL CORE COMPONENTS INSTALLED <<" in texts
    assert "custom command" in texts
    assert "Type 'activate' or 'power on' to start the neural link." not in texts


def test_workbench_complete_but_chat_phase(monkeypatch, wb_rendered,
                                           make_lab_state, required_parts,
                                           out_texts):
    monkeypatch.setattr(
        lab_d2_001, "state", make_lab_state(installed=required_parts, phase="CHAT")
    )

    lab_d2_001.workbench()

    texts = out_texts(wb_rendered["out"])
    assert ">> ALL CORE COMPONENTS INSTALLED <<" not in texts
    assert "Locate remaining 0 part(s) to complete assembly." in texts


def test_use_unknown_item(monkeypatch, assembly, make_lab_state, wb_messages):
    monkeypatch.setattr(lab_d2_001, "state", make_lab_state(installed=[]))

    lab_d2_001.use_on_workbench("nonexistent")

    assert wb_messages(assembly["workbench"]) == [
        "'nonexistent' is not a workbench component."
    ]


def test_use_item_not_in_inventory(monkeypatch, assembly, make_lab_state, wb_messages):
    monkeypatch.setattr(lab_d2_001, "state", make_lab_state(installed=[]))

    lab_d2_001.use_on_workbench("chassis_frame")

    assert wb_messages(assembly["workbench"]) == [
        "You currently do not have Robot Chassis Frame in your inventory."
    ]


def test_use_non_required_item(monkeypatch, assembly, make_lab_state, wb_messages):
    monkeypatch.setattr(
        lab_d2_001, "state", make_lab_state(installed=[], inventory=["keycard_lvl1"])
    )

    lab_d2_001.use_on_workbench("keycard_lvl1")

    assert wb_messages(assembly["workbench"]) == [
        "'Level-1 Staff Keycard' is not a workbench component."
    ]


def test_use_already_installed(monkeypatch, assembly, make_lab_state, wb_messages):
    monkeypatch.setattr(
        lab_d2_001,
        "state",
        make_lab_state(installed=["chassis_frame"], inventory=["chassis_frame"]),
    )

    lab_d2_001.use_on_workbench("chassis_frame")

    assert wb_messages(assembly["workbench"]) == [
        "'Robot Chassis Frame' is already installed."
    ]


def test_use_installs_part_not_complete(monkeypatch, assembly, make_lab_state, wb_messages):
    state = make_lab_state(installed=[], inventory=["chassis_frame"])
    monkeypatch.setattr(lab_d2_001, "state", state)

    lab_d2_001.use_on_workbench("chassis_frame")

    assert wb_messages(assembly["workbench"]) == [
        "Robot Chassis Frame installed (1/2)."
    ]
    assert state["player"]["inventory"] == []
    assert state["workbench"]["installed_parts"] == ["chassis_frame"]
    assert state["workbench"]["is_ready"] is False
    assert state["game_state"]["phase"] == "EXPLORATION"


def test_use_installs_last_part_completes(monkeypatch, assembly, make_lab_state, wb_messages):
    state = make_lab_state(installed=["chassis_frame"], inventory=["battery_pack"])
    monkeypatch.setattr(lab_d2_001, "state", state)

    lab_d2_001.use_on_workbench("battery_pack")

    messages = wb_messages(assembly["workbench"])
    assert len(messages) == 1
    assert "ALL COMPONENTS INSTALLED" in messages[0]
    assert state["player"]["inventory"] == []
    assert state["workbench"]["installed_parts"] == [
        "chassis_frame",
        "battery_pack",
    ]
    assert state["workbench"]["is_ready"] is True
    assert state["game_state"]["phase"] == "ASSEMBLY"


def test_activate_incomplete(monkeypatch, activate_env, make_lab_state,
                             wb_messages):
    monkeypatch.setattr(lab_d2_001, "state", make_lab_state(installed=[]))

    lab_d2_001.activate()

    assert wb_messages(activate_env["workbench"]) == [
        "Assembly incomplete. 2 part(s) missing."
    ]
    activate_env["prompt"].assert_not_called()
    activate_env["clear"].assert_not_called()


def test_activate_wrong_password(monkeypatch, activate_env, make_lab_state,
                                 required_parts, wb_messages):
    monkeypatch.setattr(
        lab_d2_001, "state", make_lab_state(installed=required_parts)
    )
    activate_env["prompt"].return_value = "wrong-password"

    lab_d2_001.activate()

    assert wb_messages(activate_env["workbench"]) == [
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
def test_activate_success(monkeypatch, activate_env, name_input, expected_name,
                          make_lab_state, required_parts, wifi_password,
                          wb_messages):
    state = make_lab_state(installed=required_parts)
    monkeypatch.setattr(lab_d2_001, "state", state)
    activate_env["prompt"].side_effect = [wifi_password, name_input]

    lab_d2_001.activate()

    assert state["game_state"]["phase"] == "CHAT"
    assert state["game_state"]["phases"]["chat"]["robot"]["name"] == expected_name

    assert activate_env["prompt"].call_count == 2
    assert activate_env["clear"].call_count == 2
    activate_env["render"].assert_called_once_with(
        f"INITIALIZING {expected_name.upper()}..."
    )
    activate_env["time"].sleep.assert_called_once_with(2)

    messages = wb_messages(activate_env["workbench"])
    assert messages[0] == "Enter wifi password to continue."
    assert messages[1] == "Give your robot a name. Default name is Jarvis."


def test_activate_records_weighted_score(monkeypatch, activate_env,
                                         make_lab_state, required_parts,
                                         wifi_password):
    state = make_lab_state(
        installed=required_parts,
        player_id=7,
        room_count=5,
        total_time="0:30:00",
        assembly_time="0:05:00",
    )
    monkeypatch.setattr(lab_d2_001, "state", state)
    activate_env["prompt"].side_effect = [wifi_password, "Bob"]

    lab_d2_001.activate()

    activate_env["create_scoreboard_entry"].assert_called_once_with(
        user_id=7,
        score=680,
        avg_room_time="0:05:00",
        exploration_time="0:25:00",
        assembly_time="0:05:00",
    )


def test_activate_skips_scoreboard_for_guest(monkeypatch, activate_env,
                                             make_lab_state, required_parts,
                                             wifi_password):
    state = make_lab_state(
        installed=required_parts,
        player_id=None,
        total_time="0:10:00",
        assembly_time="0:01:00",
    )
    monkeypatch.setattr(lab_d2_001, "state", state)
    activate_env["prompt"].side_effect = [wifi_password, "Bob"]

    lab_d2_001.activate()

    activate_env["create_scoreboard_entry"].assert_not_called()
