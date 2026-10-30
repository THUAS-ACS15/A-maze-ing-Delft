"""Tests for local scoreboard persistence and ordering."""

from utilities import scoreboard


def test_scoreboard_entries_are_sorted_by_exploration_then_time(monkeypatch, tmp_path):
    """Rank higher exploration first and faster equal scores first."""
    monkeypatch.chdir(tmp_path)
    scoreboard.recreate_scoreboard_table()

    scoreboard.add_scoreboard_entry("Slow complete", 100.0, 90.0)
    scoreboard.add_scoreboard_entry("Fast partial", 75.0, 10.0)
    scoreboard.add_scoreboard_entry("Fast complete", 100.0, 45.0)

    assert scoreboard.get_scoreboard_entries() == [
        ("Fast complete", 100.0, 45.0),
        ("Slow complete", 100.0, 90.0),
        ("Fast partial", 75.0, 10.0),
    ]


def test_scoreboard_time_formatting_handles_boundaries():
    """Format short, minute, hour, and negative durations consistently."""
    assert scoreboard._format_time_played(-1) == "0s"
    assert scoreboard._format_time_played(60) == "60s"
    assert scoreboard._format_time_played(61) == "1m 1s"
    assert scoreboard._format_time_played(3600) == "60m 0s"
    assert scoreboard._format_time_played(3601) == "1h 0m 1s"