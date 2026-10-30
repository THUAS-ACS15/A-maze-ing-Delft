"""Tests for status-bar time, exploration, and room rendering."""

import os

from utilities import status_bar


def test_calculate_time_played_formats_elapsed_time(monkeypatch):
    """Use the active session duration and preserve the paused label."""
    monkeypatch.setattr(status_bar.time, "time", lambda: 1061.2)

    assert status_bar.calculate_time_played(1000.0, 0.0, False) == "1m 2s"
    assert status_bar.calculate_time_played(1000.0, 3600.0, False) == "1h 1m 2s"
    assert status_bar.calculate_time_played(1000.0, 0.0, True) == "Paused"


def test_get_exploration_percent_counts_completed_rooms():
    """Return the percentage represented by truthy completed-room flags."""
    state = {"completed": {"frontdesk": True, "teachersroom1": False, "labd2001": True}}

    assert status_bar.get_exploration_percent(state) == 66.67


def test_update_status_bar_renders_room_completion(monkeypatch, capsys):
    """Render the room name, exploration percentage, completion, and time."""
    monkeypatch.setattr(status_bar, "calculate_time_played", lambda *args: "12s")
    monkeypatch.setattr(status_bar.shutil, "get_terminal_size", lambda **kwargs: os.terminal_size((120, 20)))
    monkeypatch.setattr(status_bar, "display_top_bar", lambda console: None)
    state = {
        "current_room": "frontdesk",
        "start_time": 1000.0,
        "time_elapsed": 0.0,
        "is_gametime_paused": False,
        "completed": {"frontdesk": True, "labd2001": False},
    }

    status_bar.update_status_bar(state, header_message="ready")

    output = capsys.readouterr().out
    assert "Front Desk" in output
    assert "50.0% explored" in output
    assert "Room complete!" in output
    assert "ready" in output
    assert "12s" in output