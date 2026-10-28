from io import StringIO
from unittest.mock import Mock

import pytest
from rich.console import Console

from src.rooms import teachers_room_4


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


def test_filesystem_contains_secret_path():
    shell = teachers_room_4.VirtualShell(teachers_room_4.FILESYSTEM)
    result = shell.execute(f"cat {teachers_room_4.SECRET_PATH}")
    assert teachers_room_4.SECRET_PATH in result.read_paths


def test_secret_file_awards_key_once(terminal_state):
    outputs = []
    commands = iter([f"cat {teachers_room_4.SECRET_PATH}", "exit"])
    shell = teachers_room_4.VirtualShell(teachers_room_4.FILESYSTEM)

    teachers_room_4.run_shell(
        shell,
        read_input=lambda _: next(commands),
        write_output=outputs.append,
        clear_screen=lambda: None,
    )

    assert terminal_state["player"]["inventory"] == ["secret_key"]
    assert terminal_state["flags"]["tr4_secret_key_copied"] is True
    assert any("Secret Key" in line for line in outputs)


def test_secret_file_does_not_duplicate(terminal_state):
    terminal_state["player"]["inventory"] = ["secret_key"]
    outputs = []
    commands = iter([f"cat {teachers_room_4.SECRET_PATH}", "exit"])
    shell = teachers_room_4.VirtualShell(teachers_room_4.FILESYSTEM)

    teachers_room_4.run_shell(
        shell,
        read_input=lambda _: next(commands),
        write_output=outputs.append,
        clear_screen=lambda: None,
    )

    assert terminal_state["player"]["inventory"] == ["secret_key"]
    assert terminal_state["flags"]["tr4_secret_key_copied"] is True


def test_eof_exits_cleanly(terminal_state):
    outputs = []
    shell = teachers_room_4.VirtualShell(teachers_room_4.FILESYSTEM)

    def eof(_prompt):
        raise EOFError

    teachers_room_4.run_shell(
        shell,
        read_input=eof,
        write_output=outputs.append,
        clear_screen=lambda: None,
    )

    assert outputs == [""]


def test_clear_command_clears_screen(terminal_state):
    commands = iter(["clear", "exit"])
    clear_mock = Mock()
    shell = teachers_room_4.VirtualShell(teachers_room_4.FILESYSTEM)

    teachers_room_4.run_shell(
        shell,
        read_input=lambda _: next(commands),
        write_output=lambda _: None,
        clear_screen=clear_mock,
    )

    clear_mock.assert_called_once_with()


def test_inspect_computer_rebases_timer_while_paused(
    monkeypatch, terminal_state
):
    events = []
    terminal_state["game_state"]["duration"]["pause"] = False
    monkeypatch.setattr(teachers_room_4, "loader", Mock())
    monkeypatch.setattr(teachers_room_4, "clear", Mock())
    monkeypatch.setattr(teachers_room_4.time, "sleep", lambda _: None)
    monkeypatch.setattr(teachers_room_4, "console", Mock())
    monkeypatch.setattr(teachers_room_4, "run_shell", Mock())
    monkeypatch.setattr(
        teachers_room_4,
        "auto",
        Mock(
            side_effect=lambda: events.append(
                ("auto", terminal_state["game_state"]["duration"]["pause"])
            )
        ),
    )
    monkeypatch.setattr(
        teachers_room_4,
        "render",
        Mock(
            side_effect=lambda: events.append(
                ("render", terminal_state["game_state"]["duration"]["pause"])
            )
        ),
    )

    teachers_room_4.inspect_computer()

    assert events == [("auto", True), ("render", False)]
    assert terminal_state["game_state"]["duration"]["pause"] is False


def test_shell_output_is_rendered_literally(monkeypatch, terminal_state):
    buffer = StringIO()
    monkeypatch.setattr(teachers_room_4, "console", Console(file=buffer, force_terminal=False, width=200))
    commands = iter(["cat /home/teacher/Downloads/lecture_slides.pdf", "exit"])
    shell = teachers_room_4.VirtualShell(teachers_room_4.FILESYSTEM)

    teachers_room_4.run_shell(shell, read_input=lambda _: next(commands), clear_screen=lambda: None)

    assert "[binary data omitted]" in buffer.getvalue()
