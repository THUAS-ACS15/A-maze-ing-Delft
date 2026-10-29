"""Tests for Teacher Room 4's NixOS terminal challenge.

The room computer boots a virtual shell over an in-memory filesystem. Reading
the hidden secret file awards the Encrypted API & Prompt USB exactly once and
advances the player's objective.
"""

from rooms import teachersroom4
from utilities.shell import VirtualShell


def make_state():
    """Build the minimal game state the room logic touches."""
    return {
        "inventory": [],
        "current_objective_id": 4,
        "completed": {"teachersroom4": False},
        "is_gametime_paused": False,
    }


def run_session(state, commands):
    """Run one shell session with scripted input and no screen clearing."""
    scripted = iter(commands)
    teachersroom4.run_shell(
        state,
        VirtualShell(teachersroom4.FILESYSTEM),
        read_input=lambda prompt: next(scripted),
        write_output=lambda *args: None,
        clear_screen=lambda: None,
    )


def test_secret_directory_hidden_from_plain_ls():
    shell = VirtualShell(teachersroom4.FILESYSTEM)
    assert ".secret" not in shell.execute("ls").output
    assert ".secret" in shell.execute("ls -a").output


def test_cat_secret_file_reports_read_path():
    shell = VirtualShell(teachersroom4.FILESYSTEM)
    result = shell.execute(f"cat {teachersroom4.SECRET_PATH}")
    assert result.read_paths == (teachersroom4.SECRET_PATH,)


def test_run_shell_awards_usb_on_secret_read():
    state = make_state()
    run_session(state, [f"cat {teachersroom4.SECRET_PATH}", "exit"])

    assert teachersroom4.REWARD_ITEM in state["inventory"]
    assert state["current_objective_id"] == 5
    assert state["completed"]["teachersroom4"] is True


def test_run_shell_awards_usb_only_once():
    state = make_state()
    for _ in range(2):
        run_session(state, [f"cat {teachersroom4.SECRET_PATH}", "exit"])

    assert state["inventory"].count(teachersroom4.REWARD_ITEM) == 1
    assert state["current_objective_id"] == 5


def test_run_shell_exits_cleanly():
    state = make_state()
    run_session(state, ["exit"])

    assert state["inventory"] == []
    assert state["current_objective_id"] == 4


def test_enter_teachers_room4_is_callable():
    assert callable(teachersroom4.enter_teachers_room4)
